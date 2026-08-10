#!/usr/bin/env python3
"""Build the minimal, non-secret payload mirrored into Google Master DB."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]


def load(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def build(status: dict[str, Any], health: dict[str, Any], workflow_run: str = "") -> dict[str, Any]:
    heartbeat = status
    summary = health.get("summary", {}) if isinstance(health, dict) else {}
    return {
        "operating_mode": "HYBRID_B2B",
        "source_of_truth": "GITHUB_APPROVED_SNAPSHOT",
        "engine_version": status.get("version", "2.0.0"),
        "last_run_at": status.get("last_run_at") or status.get("updated_at", ""),
        "last_success_at": status.get("last_success_at", ""),
        "last_content_change_at": status.get("last_content_change_at") or status.get("updated_at", ""),
        "published_count": status.get("items_published_current", status.get("counts", {}).get("auto_published", 0)),
        "review_count": status.get("review_queue_current", status.get("counts", {}).get("review_queue", 0)),
        "sources_success": status.get("sources_success", 0),
        "sources_failed": status.get("sources_failed", len(status.get("failures", []))),
        "health_status": health.get("status", status.get("status", "unknown")),
        "latest_workflow_run": workflow_run or status.get("workflow_run_id", ""),
        "latest_snapshot": status.get("semantic_digest", ""),
        "semantic_digest": status.get("semantic_digest", ""),
        "execution_duration_seconds": status.get("execution_duration_seconds", ""),
        "health_warnings": summary.get("warnings", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--workflow-run", default=os.environ.get("GITHUB_RUN_ID", ""))
    args = parser.parse_args()
    payload = build(
        load(ROOT / "docs/data/update_status.json", {}),
        load(ROOT / "docs/data/platform_health.json", {}),
        args.workflow_run,
    )
    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
