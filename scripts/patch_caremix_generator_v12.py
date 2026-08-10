#!/usr/bin/env python3
"""Idempotently align the Care Mix PDF generator with pricing basis v1.2."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "scripts" / "generate_caremix_specification_pdf.py"

REPLACEMENTS = {
    "Pricing basis v1.1": "Pricing basis v1.2",
    "기술·사업 사양서 v1.1": "기술·사업 사양서 v1.2",
    "PRICING BASIS v1.1": "PRICING BASIS v1.2",
    "잠정 원료 기준가<br/>실제 구매 견적으로 확정": "사용자 확정 공개 기준<br/>VAT·운송 등 별도",
    "잠정 기준 - 견적 필요": "사용자 확정 공개 기준",
    "잠정 - 구매견적 필요": "사용자 확정 공개 기준",
    "미네랄매트릭스 실제 구매단가가 확정되면 Care Mix 원료비를 자동 재산정합니다.": "미네랄매트릭스 기준가 또는 배합비가 변경되면 Care Mix 원료비를 같은 버전으로 재산정합니다.",
    "for mineral in [2000, 2500, 3000, 3500, 4000, 5000]:": "for mineral in [3000, 4000, 5000, 6000, 7000]:",
    "미네랄매트릭스 {mineral_price:,}원/kg 가정 → Care Mix 원료비 {caremix_cost:,}원/kg": "미네랄매트릭스 {mineral_price:,}원/kg 기준 → Care Mix 원료비 {caremix_cost:,}원/kg",
    "미네랄 단가는 확정 견적이 아니므로, 구매견적 수령 시 본 표와 웹·PDF·견적 템플릿을 함께 갱신합니다.": "기준가 또는 배합비가 변경되면 본 표와 웹·PDF·견적 템플릿을 같은 버전으로 갱신합니다.",
    "본 문서는 2026-08-10 기준 가격 산술 정정본 v1.1입니다.": "본 문서는 2026-08-10 기준 가격 산술 정정본 v1.2입니다.",
    "미네랄매트릭스 {mineral_price:,}원/kg은 현재 산술을 위한 잠정 기준이며,": "미네랄매트릭스 {mineral_price:,}원/kg도 사용자 확정 공개 기준이며,",
}

REQUIRED = [
    "Pricing basis v1.2",
    "PRICING BASIS v1.2",
    "for mineral in [3000, 4000, 5000, 6000, 7000]:",
    "사용자 확정 공개 기준",
]
FORBIDDEN = [
    "Pricing basis v1.1",
    "PRICING BASIS v1.1",
    "잠정 원료 기준가",
    "잠정 - 구매견적 필요",
    "현재 산술을 위한 잠정 기준",
]


def patch(text: str) -> str:
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    return text


def validate(text: str) -> None:
    missing = [item for item in REQUIRED if item not in text]
    stale = [item for item in FORBIDDEN if item in text]
    if missing or stale:
        raise ValueError(f"Care Mix generator validation failed; missing={missing}; stale={stale}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    original = TARGET.read_text(encoding="utf-8")
    updated = patch(original)
    validate(updated)

    if args.check:
        if updated != original:
            raise SystemExit("Care Mix PDF generator requires v1.2 patch")
        print("Care Mix PDF generator is aligned with v1.2")
        return 0

    if updated != original:
        TARGET.write_text(updated, encoding="utf-8")
        print("patched Care Mix PDF generator to v1.2")
    else:
        print("Care Mix PDF generator already aligned")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
