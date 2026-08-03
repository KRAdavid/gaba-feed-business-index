#!/usr/bin/env python3
"""Deployment-level checks for the public GABA index."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
REQUIRED_FILES = (
    DOCS / "index.html",
    DOCS / "404.html",
    DOCS / ".nojekyll",
    DOCS / "assets" / "styles.css",
    DOCS / "assets" / "app.js",
    DOCS / "data" / "index.json",
)
DOWNLOAD_PAIRS = (
    (ROOT / "GABA_Index_Master.xlsx", DOCS / "downloads" / "GABA_Index_Master.xlsx"),
    (ROOT / "GABA_Feed_Business_Model_Speech_Deck_v1.pptx", DOCS / "downloads" / "GABA_Feed_Business_Model_Speech_Deck_v1.pptx"),
    (ROOT / "GABA_Index_운영가이드.md", DOCS / "downloads" / "GABA_Index_운영가이드.md"),
)
EXPECTED_LIVE_SOURCES = {"mafra_rss", "europe_pmc", "world_bank_pink_sheet"}
DISCOURAGED_PUBLIC_TERMS = (
    "열린 게이트",
    "닫혀야",
    "잠가야",
    "잠금 해제",
    "해제 근거",
    "네 문이 닫히",
)


class IndexHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.section_ids: list[str] = []
        self.references: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"] or "")
        if tag == "section":
            self.section_ids.append(attributes.get("id", ""))
        if tag in {"script", "link"}:
            reference = attributes.get("src") or attributes.get("href")
            if reference:
                self.references.append(reference)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate(max_age_hours: float | None = None) -> list[str]:
    errors: list[str] = []
    for path in REQUIRED_FILES:
        if not path.exists():
            errors.append(f"required public file is missing: {path.relative_to(ROOT)}")

    if errors:
        return errors

    parser = IndexHTMLParser()
    html = (DOCS / "index.html").read_text(encoding="utf-8")
    public_copy = html + "\n" + (DOCS / "assets" / "app.js").read_text(encoding="utf-8")
    for term in DISCOURAGED_PUBLIC_TERMS:
        if term in public_copy:
            errors.append(f"discouraged public wording is present: {term}")
    parser.feed(html)
    required_ids = {"main", "readiness", "signals", "economics", "roadmap", "downloads", "appendix"}
    for missing in sorted(required_ids - parser.ids):
        errors.append(f"required HTML id is missing: {missing}")
    if not parser.section_ids or parser.section_ids[-1] != "appendix":
        errors.append("Appendix must be the final section in <main>")
    for reference in parser.references:
        if reference.startswith(("data:", "http://", "https://")):
            continue
        target = DOCS / reference.split("?", 1)[0].split("#", 1)[0]
        if not target.exists():
            errors.append(f"HTML asset reference is missing: {reference}")

    for source, public_copy in DOWNLOAD_PAIRS:
        if not source.exists() or not public_copy.exists():
            errors.append(f"download pair is incomplete: {source.name}")
        elif sha256(source) != sha256(public_copy):
            errors.append(f"public download is not synchronized: {source.name}")

    data = json.loads((DOCS / "data" / "index.json").read_text(encoding="utf-8"))
    generated_at = datetime.fromisoformat(data["meta"]["generated_at"].replace("Z", "+00:00"))
    if max_age_hours is not None:
        age_hours = (datetime.now(timezone.utc) - generated_at).total_seconds() / 3600
        if age_hours < -1:
            errors.append("generated_at is unexpectedly in the future")
        if age_hours > max_age_hours:
            errors.append(f"public snapshot is stale: {age_hours:.1f} hours old")

    health = data.get("automation", {}).get("source_health", [])
    health_sources = {row.get("source") for row in health}
    for source in sorted(EXPECTED_LIVE_SOURCES - health_sources):
        errors.append(f"live source health is missing: {source}")
    for row in health:
        if row.get("status") not in {"ok", "stale", "offline"}:
            errors.append(f"invalid source health status: {row.get('source')}")

    market = data.get("market", {})
    for key in ("corn", "soybeans"):
        points = market.get(key, {}).get("points", [])
        if len(points) < 12:
            errors.append(f"market series has fewer than 12 points: {key}")

    serialized = json.dumps(data, ensure_ascii=False)
    if re.search(r"(?:[A-Za-z]:\\|file://|https?://[^/\s]+:[^@/\s]+@)", serialized):
        errors.append("public JSON contains a local path or credential-bearing URL")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-age-hours", type=float)
    args = parser.parse_args()
    errors = validate(args.max_age_hours)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(json.dumps({"ok": True, "site": str(DOCS), "checks": "deployment"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
