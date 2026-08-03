#!/usr/bin/env python3
"""Validate public index invariants before deployment."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INDEX = ROOT / "docs" / "data" / "index.json"


def valid_link(value: str) -> bool:
    if value.startswith("downloads/"):
        return True
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate(data: dict) -> list[str]:
    errors: list[str] = []
    tracks = data.get("business_tracks", [])
    if [row.get("id") for row in tracks] != ["gaba_crude", "gaba_care_mix"]:
        errors.append("business_tracks must contain gaba_crude and gaba_care_mix in order")
    team = data.get("commercialization_team", [])
    if len(team) != 3 or any(not row.get("name") or not row.get("role") or not row.get("current") for row in team):
        errors.append("commercialization_team must contain three complete member records")
    partners = data.get("production_partners", [])
    partner_total = sum(row.get("capacity_value", 0) for row in partners)
    if len(partners) != 2 or partner_total != 220:
        errors.append("production_partners must contain two partners totaling 220 tons per month")
    if data.get("production_capacity_summary", {}).get("value") != partner_total:
        errors.append("production_capacity_summary is inconsistent")
    readiness = data.get("readiness", {})
    dimensions = readiness.get("dimensions", [])
    score = readiness.get("score")
    max_score = readiness.get("max_score")
    if len(dimensions) != 5:
        errors.append("readiness.dimensions must contain exactly five dimensions")
    if score != sum(row.get("score", 0) for row in dimensions):
        errors.append("readiness.score must equal the sum of dimension scores")
    if max_score != sum(row.get("max_score", 0) for row in dimensions):
        errors.append("readiness.max_score must equal the sum of dimension maximums")
    for row in dimensions:
        if not 0 <= row.get("score", -1) <= row.get("max_score", -1):
            errors.append(f"invalid dimension score: {row.get('id')}")
    gates = data.get("critical_gates", [])
    if len(gates) != 4:
        errors.append("critical_gates must contain exactly four gates")
    if data.get("summary", {}).get("critical_open_gates") != sum(1 for gate in gates if gate.get("status") == "OPEN"):
        errors.append("summary.critical_open_gates is inconsistent")
    try:
        datetime.fromisoformat(data["meta"]["generated_at"].replace("Z", "+00:00"))
    except (KeyError, TypeError, ValueError):
        errors.append("meta.generated_at must be an ISO-8601 timestamp")
    signals = data.get("signals", [])
    seen_ids: set[str] = set()
    for signal in signals:
        missing = [field for field in ("id", "date", "category", "title", "url", "review_status") if not signal.get(field)]
        if missing:
            errors.append(f"signal missing {','.join(missing)}: {signal.get('id', '<no-id>')}")
        if signal.get("id") in seen_ids:
            errors.append(f"duplicate signal id: {signal.get('id')}")
        seen_ids.add(signal.get("id"))
        if signal.get("review_status") not in {"reviewed", "auto-collected"}:
            errors.append(f"invalid review_status: {signal.get('id')}")
        if signal.get("url") and not valid_link(signal["url"]):
            errors.append(f"invalid signal URL: {signal.get('id')}")
    reviewed = sum(1 for row in signals if row.get("review_status") == "reviewed")
    auto = len(signals) - reviewed
    if data.get("summary", {}).get("reviewed_signals") != reviewed:
        errors.append("summary.reviewed_signals is inconsistent")
    if data.get("summary", {}).get("auto_signals_waiting_review") != auto:
        errors.append("summary.auto_signals_waiting_review is inconsistent")
    for source in data.get("source_catalog", []):
        if not valid_link(source.get("url", "")):
            errors.append(f"invalid source URL: {source.get('id')}")
    for download in data.get("downloads", []):
        if not valid_link(download.get("file", "")):
            errors.append(f"invalid download path: {download.get('name')}")
    return errors


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("index", nargs="?", type=Path, default=DEFAULT_INDEX)
    args = parser.parse_args()
    data = json.loads(args.index.read_text(encoding="utf-8"))
    errors = validate(data)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(json.dumps({"ok": True, "index": str(args.index), "signals": len(data.get("signals", [])), "score": data["readiness"]["score"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
