#!/usr/bin/env python3
"""Validate the evidence publication gate without inventing research claims."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "data" / "evidence_claim_matrix.json"
REQUIRED_DOCUMENTS = {
    "pig-gaba-feed-proposal",
    "australia-wagyu-gaba-assessment",
    "stress-care-gaba-feed-proposal",
}


def validate(payload: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    documents = {row.get("document_id"): row for row in payload.get("documents", [])}
    missing = REQUIRED_DOCUMENTS - set(documents)
    if missing:
        errors.append("missing review documents: " + ", ".join(sorted(missing)))
    for document_id, row in documents.items():
        if row.get("status") != "Review" or row.get("public") is not False:
            errors.append(f"document is not held in Review/public=false: {document_id}")

    claims = payload.get("claims", [])
    red = [row.get("claim_id") for row in claims if row.get("qa_status") == "RED"]
    if red:
        errors.append("RED claims must be zero: " + ", ".join(red))
    for row in claims:
        if not row.get("source"):
            errors.append(f"claim has unidentified source: {row.get('claim_id')}")
        if row.get("public") is True and row.get("qa_status") != "GREEN":
            errors.append(f"non-GREEN claim is public: {row.get('claim_id')}")
        if row.get("dose") and not row.get("dose_standardized"):
            errors.append(f"dose is not standardized: {row.get('claim_id')}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", type=Path, default=MATRIX)
    args = parser.parse_args()
    payload = json.loads(args.path.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        for error in errors:
            print("ERROR:", error)
        return 1
    print(json.dumps({
        "ok": True,
        "documents": len(payload.get("documents", [])),
        "claims": len(payload.get("claims", [])),
        "red_claims": 0,
        "public_claims": sum(1 for row in payload.get("claims", []) if row.get("public") is True),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
