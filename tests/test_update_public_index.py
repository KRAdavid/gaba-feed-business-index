from __future__ import annotations

import json
import io
import sys
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import update_public_index as updater  # noqa: E402
from validate_public_index import validate  # noqa: E402


FIXTURES = ROOT / "tests" / "fixtures"


class UpdatePublicIndexTests(unittest.TestCase):
    def test_mafra_parser_filters_irrelevant_items(self) -> None:
        rows = updater.parse_mafra_rss((FIXTURES / "mafra.xml").read_bytes())
        self.assertEqual(len(rows), 1)
        self.assertIn("사료", rows[0]["title"])
        self.assertEqual(rows[0]["review_status"], "auto-collected")

    def test_europe_pmc_parser_requires_gaba_and_animal_context(self) -> None:
        rows = updater.parse_europe_pmc((FIXTURES / "europepmc.json").read_bytes())
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["doi"], "10.1234/gaba-feed")

    def test_market_summary_from_world_bank_xlsx(self) -> None:
        workbook = io.BytesIO()
        with zipfile.ZipFile(workbook, "w") as archive:
            archive.writestr(
                "xl/workbook.xml",
                '<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets><sheet name="Monthly Prices" sheetId="1" r:id="rId1"/></sheets></workbook>',
            )
            archive.writestr(
                "xl/_rels/workbook.xml.rels",
                '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Target="worksheets/sheet1.xml" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet"/></Relationships>',
            )
            archive.writestr(
                "xl/worksheets/sheet1.xml",
                '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>'
                '<row r="5"><c r="A5" t="inlineStr"><is><t>Date</t></is></c><c r="B5" t="inlineStr"><is><t>Soybeans</t></is></c><c r="C5" t="inlineStr"><is><t>Maize</t></is></c></row>'
                '<row r="7"><c r="A7" t="inlineStr"><is><t>2026M01</t></is></c><c r="B7"><v>400</v></c><c r="C7"><v>200</v></c></row>'
                '<row r="8"><c r="A8" t="inlineStr"><is><t>2026M02</t></is></c><c r="B8"><v>420</v></c><c r="C8"><v>210</v></c></row>'
                '<row r="9"><c r="A9" t="inlineStr"><is><t>2026M03</t></is></c><c r="B9"><v>430</v></c><c r="C9"><v>220.5</v></c></row>'
                '</sheetData></worksheet>',
            )
        summary = updater.parse_world_bank_xlsx(workbook.getvalue())["corn"]
        self.assertEqual(summary["latest"], 220.5)
        self.assertEqual(summary["mom_pct"], 5.0)
        self.assertEqual(summary["signal"], "원료비 상승 요인")

    def test_world_bank_workbook_discovery(self) -> None:
        html = b'<a href="/data/CMO-Historical-Data-Monthly.xlsx">Monthly</a>'
        self.assertEqual(
            updater.discover_world_bank_xlsx(html, "https://example.com/market"),
            "https://example.com/data/CMO-Historical-Data-Monthly.xlsx",
        )

    def test_offline_build_preserves_score_and_validates(self) -> None:
        base = json.loads((ROOT / "data" / "base_index.json").read_text(encoding="utf-8"))
        manual = json.loads((ROOT / "data" / "manual_signals.json").read_text(encoding="utf-8"))
        output = updater.build_index(base, manual, previous={}, offline=True)
        self.assertEqual(output["readiness"]["score"], 41)
        self.assertEqual(validate(output), [])


if __name__ == "__main__":
    unittest.main()
