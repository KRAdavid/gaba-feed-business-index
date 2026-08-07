#!/usr/bin/env python3
"""Run the intelligence engine after selecting a reachable official URL per source.

The canonical config keeps ordered `urls`. This wrapper probes each official URL,
temporarily selects the first reachable route, runs the existing conservative
collector, restores the canonical config and writes non-sensitive route status
into the public update-status snapshot.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "intelligence_sources_v2.json"
STATUS = ROOT / "docs" / "data" / "update_status.json"
ENGINE = ROOT / "scripts" / "auto_intelligence_v2.py"
USER_AGENT = "Cellpinda-GABA-Feed-Intelligence/2.1 (+https://github.com/KRAdavid/gaba-feed-business-index)"


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def probe(url: str, timeout: int = 18) -> tuple[bool, str]:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/json;q=0.9,*/*;q=0.7",
            "Range": "bytes=0-65535",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            status = int(getattr(response, "status", 200) or 200)
            response.read(2048)
            return 200 <= status < 400, f"HTTP {status}"
    except urllib.error.HTTPError as error:
        return False, f"HTTP {error.code}"
    except Exception as error:  # route selection must not abort the full run
        return False, str(error)[:180]


def choose_routes(config: dict[str, Any]) -> list[dict[str, Any]]:
    reports: list[dict[str, Any]] = []
    for source in config.get("official_monitors", []):
        urls = [str(url).strip() for url in (source.get("urls") or [source.get("url")]) if str(url).strip()]
        attempts: list[dict[str, str | bool]] = []
        selected = ""
        for url in urls:
            ok, result = probe(url)
            attempts.append({"url": url, "ok": ok, "result": result})
            if ok:
                selected = url
                break
        if selected:
            source["url"] = selected
        reports.append({
            "source": source.get("id", source.get("name", "unknown")),
            "selected_url": selected,
            "reachable": bool(selected),
            "attempts": attempts,
        })
    return reports


def update_public_status(reports: list[dict[str, Any]]) -> None:
    payload = load_json(STATUS, {})
    payload["route_checked_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload["source_routes"] = [
        {
            "source": report["source"],
            "reachable": report["reachable"],
            "selected_url": report["selected_url"],
            "attempt_count": len(report["attempts"]),
            "last_result": report["attempts"][-1]["result"] if report["attempts"] else "no URL",
        }
        for report in reports
    ]
    save_json(STATUS, payload)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--since-days", type=int, default=30)
    parser.add_argument("--probe-only", action="store_true")
    args = parser.parse_args()

    canonical_text = CONFIG.read_text(encoding="utf-8")
    config = json.loads(canonical_text)
    reports = choose_routes(config)

    print(json.dumps(reports, ensure_ascii=False, indent=2))
    if args.probe_only:
        return 0 if all(report["reachable"] for report in reports) else 2

    try:
        save_json(CONFIG, config)
        completed = subprocess.run(
            [sys.executable, str(ENGINE), "--since-days", str(max(1, min(args.since_days, 365)))],
            cwd=ROOT,
            check=False,
        )
        update_public_status(reports)
        return completed.returncode
    finally:
        CONFIG.write_text(canonical_text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
