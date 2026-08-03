#!/usr/bin/env python3
"""Build the public GABA Feed Business Model Index from reviewed and live sources.

Automatic items are discovery signals only. They never change readiness scores;
the score remains governed by reviewed evidence in data/base_index.json.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import io
import json
import os
import posixpath
import re
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BASE = ROOT / "data" / "base_index.json"
DEFAULT_SIGNALS = ROOT / "data" / "manual_signals.json"
DEFAULT_OUTPUT = ROOT / "docs" / "data" / "index.json"

MAFRA_RSS = "https://www.mafra.go.kr/bbs/home/792/rssList.do?row=50"
EUROPE_PMC_API = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
WORLD_BANK_MARKET_PAGE = "https://www.worldbank.org/en/research/commodity-markets"
WORLD_BANK_MARKET_SERIES = {
    "corn": {
        "name": "국제 옥수수 가격",
        "series_id": "World Bank Pink Sheet: Maize",
        "column": "Maize",
        "source_url": WORLD_BANK_MARKET_PAGE,
        "unit": "USD/metric ton",
    },
    "soybeans": {
        "name": "국제 대두 가격",
        "series_id": "World Bank Pink Sheet: Soybeans",
        "column": "Soybeans",
        "source_url": WORLD_BANK_MARKET_PAGE,
        "unit": "USD/metric ton",
    },
}

POLICY_KEYWORDS = (
    "사료",
    "축산",
    "가축",
    "저탄소",
    "메탄",
    "질소",
    "배합",
    "동물용의약품",
    "동물복지",
    "방역",
    "원료",
)
GABA_TERMS = ("gaba", "gamma-aminobutyric", "gamma aminobutyric", "γ-aminobutyric")
ANIMAL_TERMS = (
    "feed",
    "livestock",
    "animal",
    "cattle",
    "cow",
    "dairy",
    "bovine",
    "rumen",
    "steer",
    "pig",
    "swine",
    "poultry",
    "broiler",
    "hen",
    "sheep",
    "goat",
    "fish",
    "shrimp",
    "aquaculture",
)
EUROPE_PMC_QUERY = "GABA AND (feed OR diet) AND (cattle OR dairy OR livestock OR aquaculture OR fish OR poultry OR pig OR goat OR sheep)"


def utc_now() -> datetime:
    fixed = os.environ.get("GABA_INDEX_NOW")
    if fixed:
        parsed = datetime.fromisoformat(fixed.replace("Z", "+00:00"))
        return parsed.astimezone(timezone.utc)
    return datetime.now(timezone.utc)


def load_json(path: Path, fallback: Any = None) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        if fallback is not None:
            return fallback
        raise


def fetch_bytes(url: str, *, timeout: int = 12, attempts: int = 2) -> bytes:
    headers = {
        "User-Agent": "GABA-Public-Index/1.0 (evidence-monitor; no automated scoring)",
        "Accept": "application/json, application/rss+xml, application/xml, text/xml, text/csv, text/html;q=0.8, */*;q=0.5",
    }
    last_error: Exception | None = None
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = exc
            if attempt + 1 < attempts:
                time.sleep(1.5 * (attempt + 1))
    raise RuntimeError(f"fetch failed after {attempts} attempts: {url}: {last_error}")


def clean_text(value: str | None) -> str:
    if not value:
        return ""
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(value.replace("\u00a0", " ").split())


def stable_id(prefix: str, value: str) -> str:
    return f"{prefix}-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:14]}"


def parse_date(value: str | None) -> str:
    if not value:
        return ""
    value = value.strip()
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError, OverflowError):
        pass
    match = re.search(r"(20\d{2})[-./](\d{1,2})[-./](\d{1,2})", value)
    if match:
        return f"{int(match.group(1)):04d}-{int(match.group(2)):02d}-{int(match.group(3)):02d}"
    return ""


def parse_mafra_rss(payload: bytes, limit: int = 12) -> list[dict[str, Any]]:
    root = ET.fromstring(payload)
    items: list[dict[str, Any]] = []
    for node in root.findall(".//item"):
        title = clean_text(node.findtext("title"))
        haystack = f"{title} {clean_text(node.findtext('description'))}"
        if not any(keyword in haystack for keyword in POLICY_KEYWORDS):
            continue
        link = clean_text(node.findtext("link"))
        link = urllib.parse.urljoin("https://www.mafra.go.kr", link)
        date = parse_date(node.findtext("pubDate")) or parse_date(node.findtext("date"))
        items.append(
            {
                "id": stable_id("mafra", link or title),
                "date": date,
                "category": "정책자동",
                "title": title,
                "summary": "농림축산식품부 보도자료에서 사료·축산 사업과 관련된 내용을 찾았습니다. 담당자가 원문을 확인하기 전까지는 참고 자료로만 표시합니다.",
                "judgment": "검토 대기",
                "action": "담당자가 원문을 확인한 뒤 사업에 미치는 영향과 필요한 조치를 기록합니다.",
                "source_name": "농림축산식품부 RSS",
                "url": link,
                "review_status": "auto-collected",
                "source_quality": "정부 1차 자료·자동수집",
            }
        )
        if len(items) >= limit:
            break
    return items


def parse_europe_pmc(payload: bytes, limit: int = 12) -> list[dict[str, Any]]:
    data = json.loads(payload.decode("utf-8"))
    works = data.get("resultList", {}).get("result", [])
    results: list[dict[str, Any]] = []
    for work in works:
        title = clean_text(work.get("title"))
        container = clean_text(work.get("journalTitle"))
        journal_info = work.get("journalInfo") or {}
        haystack = f"{title} {container}".lower()
        if not any(term in haystack for term in GABA_TERMS):
            continue
        if not any(term in haystack for term in ANIMAL_TERMS):
            continue
        doi = clean_text(work.get("doi"))
        record_id = clean_text(work.get("id"))
        source = clean_text(work.get("source"))
        url = f"https://doi.org/{doi}" if doi else f"https://europepmc.org/article/{source}/{record_id}"
        authors = [name.strip() for name in clean_text(work.get("authorString")).split(",") if name.strip()]
        results.append(
            {
                "id": stable_id("europepmc", doi or url or title),
                "date": parse_date(work.get("firstPublicationDate")) or parse_date(journal_info.get("printPublicationDate")),
                "category": "학술자동",
                "title": title,
                "summary": f"{container or '학술자료'}에 실린 연구를 Europe PMC에서 찾았습니다. 대상 축종, 투여 형태와 용량, 시험 설계, 통계 결과를 확인하기 전까지는 참고 자료로만 표시합니다.",
                "judgment": "검토 대기",
                "action": "원문에서 연구 대상, 투여량, 주요 결과와 한계를 확인한 뒤 제품 적용 가능성을 평가합니다.",
                "source_name": container or "Europe PMC",
                "url": url,
                "review_status": "auto-collected",
                "source_quality": "Europe PMC 메타데이터·자동수집",
                "authors": authors[:4],
                "doi": doi,
            }
        )
        if len(results) >= limit:
            break
    return results


def discover_world_bank_xlsx(payload: bytes, page_url: str = WORLD_BANK_MARKET_PAGE) -> str:
    """Find the current Pink Sheet monthly workbook without hard-coding its yearly document id."""

    html = payload.decode("utf-8", errors="ignore")
    match = re.search(
        r"href=[\"']([^\"']*CMO-Historical-Data-Monthly\.xlsx[^\"']*)",
        html,
        flags=re.IGNORECASE,
    )
    if not match:
        raise ValueError("World Bank monthly price workbook link was not found")
    return urllib.parse.urljoin(page_url, match.group(1).replace("&amp;", "&"))


def xlsx_column_index(cell_reference: str) -> int:
    letters = re.match(r"[A-Z]+", cell_reference.upper())
    if not letters:
        return -1
    number = 0
    for letter in letters.group(0):
        number = number * 26 + ord(letter) - 64
    return number - 1


def xlsx_rows(payload: bytes, sheet_name: str) -> list[list[Any]]:
    """Read values from one XLSX worksheet using only the Python standard library."""

    spreadsheet_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
    relationship_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    package_ns = "http://schemas.openxmlformats.org/package/2006/relationships"
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        relationship_id = ""
        for sheet in workbook.findall(f".//{{{spreadsheet_ns}}}sheet"):
            if sheet.get("name") == sheet_name:
                relationship_id = sheet.get(f"{{{relationship_ns}}}id", "")
                break
        if not relationship_id:
            raise ValueError(f"worksheet not found: {sheet_name}")

        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = ""
        for relationship in relationships.findall(f"{{{package_ns}}}Relationship"):
            if relationship.get("Id") == relationship_id:
                target = relationship.get("Target", "")
                break
        if not target:
            raise ValueError(f"worksheet relationship not found: {sheet_name}")
        worksheet_path = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join("xl", target))

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall(f"{{{spreadsheet_ns}}}si"):
                shared_strings.append("".join(node.text or "" for node in item.findall(f".//{{{spreadsheet_ns}}}t")))

        worksheet = ET.fromstring(archive.read(worksheet_path))
        rows: list[list[Any]] = []
        for row in worksheet.findall(f".//{{{spreadsheet_ns}}}row"):
            values: dict[int, Any] = {}
            for cell in row.findall(f"{{{spreadsheet_ns}}}c"):
                column = xlsx_column_index(cell.get("r", ""))
                if column < 0:
                    continue
                cell_type = cell.get("t", "")
                value_node = cell.find(f"{{{spreadsheet_ns}}}v")
                if cell_type == "inlineStr":
                    value: Any = "".join(node.text or "" for node in cell.findall(f".//{{{spreadsheet_ns}}}t"))
                elif value_node is None:
                    value = None
                elif cell_type == "s":
                    try:
                        value = shared_strings[int(value_node.text or "-1")]
                    except (IndexError, ValueError):
                        value = None
                elif cell_type in {"str", "e"}:
                    value = value_node.text or ""
                else:
                    raw = value_node.text or ""
                    try:
                        value = float(raw)
                    except ValueError:
                        value = raw
                values[column] = value
            if values:
                width = max(values) + 1
                rows.append([values.get(index) for index in range(width)])
        return rows


def parse_world_bank_xlsx(payload: bytes, months: int = 24) -> dict[str, Any]:
    rows = xlsx_rows(payload, "Monthly Prices")
    header: list[Any] | None = None
    data_start = 0
    required_columns = {config["column"] for config in WORLD_BANK_MARKET_SERIES.values()}
    for index, row in enumerate(rows):
        names = {str(value).strip() for value in row if value is not None}
        if required_columns.issubset(names):
            header = row
            data_start = index + 1
            break
    if header is None:
        raise ValueError("Maize and Soybeans columns were not found in the Pink Sheet")

    column_map = {str(value).strip(): index for index, value in enumerate(header) if value is not None}
    points: dict[str, list[dict[str, Any]]] = {key: [] for key in WORLD_BANK_MARKET_SERIES}
    for row in rows[data_start:]:
        if not row or not isinstance(row[0], str):
            continue
        date_match = re.fullmatch(r"(20\d{2})M(\d{2})", row[0].strip())
        if not date_match:
            continue
        date = f"{date_match.group(1)}-{date_match.group(2)}-01"
        for key, config in WORLD_BANK_MARKET_SERIES.items():
            column = column_map[config["column"]]
            if column >= len(row) or not isinstance(row[column], (int, float)):
                continue
            points[key].append({"date": date, "value": round(float(row[column]), 3)})

    return {
        key: summarize_market(key, config, points[key][-months:])
        for key, config in WORLD_BANK_MARKET_SERIES.items()
    }


def pct_change(current: float, previous: float | None) -> float | None:
    if previous in (None, 0):
        return None
    return round((current / previous - 1) * 100, 1)


def summarize_market(name: str, config: dict[str, str], points: list[dict[str, Any]]) -> dict[str, Any]:
    if not points:
        return {"name": name, **config, "points": [], "latest": None, "mom_pct": None, "yoy_pct": None, "signal": "데이터 없음"}
    current = points[-1]["value"]
    previous = points[-2]["value"] if len(points) >= 2 else None
    year_ago = points[-13]["value"] if len(points) >= 13 else None
    mom = pct_change(current, previous)
    yoy = pct_change(current, year_ago)
    if mom is None:
        signal = "변화율 계산 대기"
    elif mom >= 3:
        signal = "원료비 상승 요인"
    elif mom <= -3:
        signal = "원료비 부담 완화"
    else:
        signal = "큰 변동 없음"
    return {
        "key": name,
        "name": config["name"],
        "series_id": config["series_id"],
        "source_url": config["source_url"],
        "unit": config["unit"],
        "latest_date": points[-1]["date"],
        "latest": round(current, 2),
        "mom_pct": mom,
        "yoy_pct": yoy,
        "signal": signal,
        "points": points,
    }


def dedupe_signals(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    unique: list[dict[str, Any]] = []
    for signal in sorted(signals, key=lambda row: (row.get("date", ""), row.get("review_status") == "reviewed"), reverse=True):
        key = (signal.get("url") or signal.get("title") or signal.get("id") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(signal)
    return unique


def fetch_research(fetcher: Callable[[str], bytes]) -> list[dict[str, Any]]:
    params = urllib.parse.urlencode({"query": EUROPE_PMC_QUERY, "format": "json", "pageSize": "100"})
    rows = parse_europe_pmc(fetcher(f"{EUROPE_PMC_API}?{params}"), limit=30)
    return sorted(dedupe_signals(rows), key=lambda row: row.get("date", ""), reverse=True)[:12]


def health_row(source: str, status: str, fetched_at: str, count: int, error: str = "") -> dict[str, Any]:
    row = {"source": source, "status": status, "fetched_at": fetched_at, "item_count": count}
    if error:
        row["error"] = clean_text(error)[:240]
    return row


def previous_dynamic(previous: dict[str, Any], category: str) -> list[dict[str, Any]]:
    return [row for row in previous.get("signals", []) if row.get("category") == category]


def build_index(
    base: dict[str, Any],
    manual_signals: list[dict[str, Any]],
    previous: dict[str, Any] | None = None,
    fetcher: Callable[[str], bytes] = fetch_bytes,
    offline: bool = False,
) -> dict[str, Any]:
    previous = previous or {}
    now = utc_now()
    now_iso = now.isoformat(timespec="seconds").replace("+00:00", "Z")
    result = copy.deepcopy(base)
    health: list[dict[str, Any]] = []

    policy_auto: list[dict[str, Any]] = []
    research_auto: list[dict[str, Any]] = []
    market: dict[str, Any] = {}

    if offline:
        policy_auto = previous_dynamic(previous, "정책자동")
        research_auto = previous_dynamic(previous, "학술자동")
        market = copy.deepcopy(previous.get("market", {}))
        health.append(health_row("all-live-sources", "offline", now_iso, len(policy_auto) + len(research_auto)))
    else:
        def policy_task() -> list[dict[str, Any]]:
            return parse_mafra_rss(fetcher(MAFRA_RSS))

        def research_task() -> list[dict[str, Any]]:
            return fetch_research(fetcher)

        def market_task() -> dict[str, Any]:
            landing_page = fetcher(WORLD_BANK_MARKET_PAGE)
            workbook_url = discover_world_bank_xlsx(landing_page)
            return parse_world_bank_xlsx(fetcher(workbook_url))

        tasks: dict[Any, tuple[str, str | None]] = {}
        with ThreadPoolExecutor(max_workers=3) as executor:
            tasks[executor.submit(policy_task)] = ("mafra_rss", None)
            tasks[executor.submit(research_task)] = ("europe_pmc", None)
            tasks[executor.submit(market_task)] = ("world_bank_pink_sheet", "market")
            for future in as_completed(tasks):
                source, market_key = tasks[future]
                try:
                    value = future.result()
                    if source == "mafra_rss":
                        policy_auto = value
                        count = len(policy_auto)
                    elif source == "europe_pmc":
                        research_auto = value
                        count = len(research_auto)
                    else:
                        market = value
                        count = sum(len(row.get("points", [])) for row in value.values())
                    health.append(health_row(source, "ok", now_iso, count))
                except Exception as exc:  # noqa: BLE001 - stale fallback is an intentional resilience feature
                    if source == "mafra_rss":
                        policy_auto = previous_dynamic(previous, "정책자동")
                        count = len(policy_auto)
                    elif source == "europe_pmc":
                        research_auto = previous_dynamic(previous, "학술자동")
                        count = len(research_auto)
                    else:
                        market = copy.deepcopy(previous.get("market", {}))
                        count = sum(len(row.get("points", [])) for row in market.values())
                    health.append(health_row(source, "stale", now_iso, count, str(exc)))
        health.sort(key=lambda row: row["source"])

    combined_signals = dedupe_signals(manual_signals + policy_auto + research_auto)
    reviewed_count = sum(1 for row in combined_signals if row.get("review_status") == "reviewed")
    auto_count = len(combined_signals) - reviewed_count
    dimensions = result["readiness"]["dimensions"]

    result["meta"] = {
        "generated_at": now_iso,
        "as_of_date": now.date().isoformat(),
        "timezone": "Asia/Seoul",
        "automation": "Codex 주간 자동화 + Sites production 배포",
        "next_scheduled_refresh": "매주 월요일 09:17 KST",
        "public_url": "https://gaba-feed-business-index.dubaissday.chatgpt.site",
        "score_policy": "자동 수집 신호는 검토 완료 전 준비도 점수에 반영하지 않음",
    }
    result["summary"] = {
        "readiness_score": result["readiness"]["score"],
        "target_readiness_score": result["readiness"].get("target", {}).get("score", 100),
        "readiness_gap": result["readiness"].get("target", {}).get("gap", 100 - result["readiness"]["score"]),
        "stage": result["readiness"]["stage"],
        "critical_open_gates": sum(1 for gate in result["critical_gates"] if gate.get("status") == "OPEN"),
        "reviewed_signals": reviewed_count,
        "auto_signals_waiting_review": auto_count,
        "source_health_ok": sum(1 for row in health if row["status"] == "ok"),
        "source_health_total": len(health),
        "lowest_dimension": min(dimensions, key=lambda row: row["score"])["name"],
    }
    result["signals"] = combined_signals
    result["market"] = market
    result["automation"] = {
        "source_health": health,
        "last_successful_live_refresh": now_iso if any(row["status"] == "ok" for row in health) else previous.get("automation", {}).get("last_successful_live_refresh"),
        "review_queue_count": auto_count,
    }
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Update the public GABA feed business model index")
    parser.add_argument("--base", type=Path, default=DEFAULT_BASE)
    parser.add_argument("--signals", type=Path, default=DEFAULT_SIGNALS)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--offline", action="store_true", help="Reuse the previous dynamic snapshot without network calls")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base = load_json(args.base)
    signals = load_json(args.signals)
    previous = load_json(args.output, fallback={})
    index = build_index(base, signals, previous=previous, offline=args.offline)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output),
                "generated_at": index["meta"]["generated_at"],
                "signals": len(index["signals"]),
                "review_queue": index["summary"]["auto_signals_waiting_review"],
                "source_health": index["automation"]["source_health"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
