#!/usr/bin/env python3
"""Remove the obsolete broad 5,000 KRW stale-price detector.

The approved Mineral Matrix basis is now 5,000 KRW/kg, so a generic rule that
flags any 5,000 KRW value near the words Care Mix is invalid. Exact obsolete
formula detectors remain in place for the old 50:50 total and 3,000/10,500 basis.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "reconcile_caremix_pricing.py"
OBSOLETE = '        re.compile(r"가바케어믹스[^\\n<]{0,160}5,000원/kg"),\n'


def patch(text: str) -> str:
    return text.replace(OBSOLETE, "")


def validate(text: str) -> None:
    if OBSOLETE in text:
        raise ValueError("obsolete broad 5,000 KRW detector remains")
    required = [
        're.compile(r"미네랄매트릭스[^\\n<]{0,120}3,000원/kg")',
        're.compile(r"가바케어믹스[^\\n<]{0,160}10,500원/kg")',
        're.compile(r"가바크루드 50%\\s*\\+\\s*미네랄매트릭스 50%[^\\n<]{0,80}5,000원/kg")',
    ]
    missing = [item for item in required if item not in text]
    if missing:
        raise ValueError(f"specific stale-price detectors missing: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    original = TARGET.read_text(encoding="utf-8")
    updated = patch(original)
    validate(updated)

    if args.check:
        if updated != original:
            raise SystemExit("reconcile detector patch required")
        print("Care Mix stale-price detectors are specific and valid")
        return 0

    if updated != original:
        TARGET.write_text(updated, encoding="utf-8")
        print("removed obsolete broad 5,000 KRW detector")
    else:
        print("detector already corrected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
