#!/usr/bin/env python3
"""Reconcile the public Care Mix arithmetic with GABA Crude 18,000 KRW/kg.

This script is intentionally idempotent. It updates the operational source JSON,
public snapshot, public HTML and technical-document metadata from one pricing
configuration. It removes unverified public internal-cost figures rather than
presenting them as a customer-facing unit price.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "caremix_pricing_v1.json"
SOURCE_JSONS = [ROOT / "data" / "base_index.json", ROOT / "docs" / "data" / "index.json"]
PUBLIC_PRICING = ROOT / "docs" / "data" / "caremix_pricing.json"
TECH_DOCS = ROOT / "docs" / "data" / "technical_documents.json"
INDEX_HTML = ROOT / "docs" / "index.html"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def krw(value: int) -> str:
    return f"{value:,}원/kg"


def assumptions_of(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = data.get("assumptions")
    if not isinstance(rows, list):
        raise ValueError("assumptions list is missing")
    return rows


def replace_or_append(rows: list[dict[str, Any]], metric: str, row: dict[str, Any]) -> None:
    for index, current in enumerate(rows):
        if current.get("metric") == metric:
            rows[index] = row
            return
    rows.append(row)


def reconcile_assumptions(data: dict[str, Any], cfg: dict[str, Any]) -> bool:
    rows = assumptions_of(data)
    before = json.dumps(rows, ensure_ascii=False, sort_keys=True)

    # Remove the obsolete 7,000 KRW/kg internal proxy from the public model.
    rows[:] = [row for row in rows if row.get("metric") not in {
        "가바크루드 표준품 원가",
        "내부 제조 시 원가 하한 참고",
    }]

    crude = int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"])
    mineral = int(cfg["mineral_matrix"]["price_krw_per_kg"])
    caremix = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"])

    replace_or_append(rows, "가바크루드 판매가격", {
        "metric": "가바크루드 판매가격",
        "value": krw(crude),
        "state": "사용자 확정 공개 기준",
        "formula": "가바케어믹스 공개 산술에 적용; VAT·운송·고객별 거래조건 별도",
        "unlock": "고객별 유효 견적서와 거래조건",
    })
    replace_or_append(rows, "가바케어믹스 혼합비·원료 투입원가", {
        "metric": "가바케어믹스 혼합비·원료 투입원가",
        "value": f"가바크루드 50% + 미네랄매트릭스 50% · {caremix:,}원/kg",
        "state": "공개 기준가·잠정 미네랄 단가의 이론 계산",
        "formula": f"GABA 20% 가바크루드 0.5kg×{crude:,}원/kg + 미네랄매트릭스 0.5kg×{mineral:,}원/kg = {caremix:,}원/kg; 사료 1톤당 {caremix:,}원",
        "unlock": "미네랄 구매견적·제조·검사·포장·수율손실·축종별 실제 섭취량 확인",
    })
    replace_or_append(rows, "가바케어믹스 최종 매출원가·공급단가", {
        "metric": "가바케어믹스 최종 매출원가·공급단가",
        "value": "시험생산·견적 후 확정",
        "state": "계산 대기",
        "formula": f"원료 투입원가 {caremix:,}원/kg + 혼합·제조·검사·포장·수율손실·물류·거래조건",
        "unlock": "OEM 견적·시험생산 실수율·검사·포장·물류비와 고객별 공급조건",
    })

    data["pricing_reference"] = cfg
    after = json.dumps(rows, ensure_ascii=False, sort_keys=True)
    return before != after


def caremix_section(cfg: dict[str, Any]) -> str:
    crude = int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"])
    mineral = int(cfg["mineral_matrix"]["price_krw_per_kg"])
    total = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"])
    return f'''<section class="brand-evolution" id="caremix-dose" data-pricing-version="1.1" data-pricing-date="{cfg['effective_date']}"><div class="container"><div class="section-title left"><span class="product-label">PRICING BASIS · {cfg['effective_date']}</span><h2>가바케어믹스는 사료 1톤당 1kg 투입 기준으로 설계합니다</h2><p>최종 사료의 명목 GABA 100mg/kg 기준을 충족하도록 GABA 20% 가바크루드와 미네랄매트릭스를 50:50으로 배합합니다.</p></div><div class="evolution-grid"><article class="evolution-step"><span>투입 기준</span><h3>사료 1톤당 1kg</h3><p>Care Mix 1kg을 사료 1톤에 투입하는 제품 설계 기준입니다.</p></article><article class="evolution-step"><span>최종 사료 설계</span><h3>GABA 100mg/kg</h3><p>사료 1톤에 GABA 100g을 공급하는 명목 기준입니다.</p></article><article class="evolution-step"><span>혼합비</span><h3>가바크루드 50%<br>미네랄매트릭스 50%</h3><p>가바크루드 0.5kg에 GABA 100g이 포함되어 Care Mix GABA 10%를 설계합니다.</p></article><article class="evolution-step final"><span>원료 투입 이론값</span><h3>{total:,}원/kg</h3><p>가바크루드 0.5kg×{crude:,}원 + 미네랄매트릭스 0.5kg×{mineral:,}원. 사료 1톤당 {total:,}원입니다.</p></article></div><p class="story-disclaimer"><strong>가격 구분:</strong> {total:,}원/kg은 원료 2종만 반영한 이론 원료비이며 가바케어믹스 판매가격이 아닙니다. 가바크루드 공급 기준가는 {crude:,}원/kg이고, 미네랄매트릭스 {mineral:,}원/kg은 잠정 기준입니다. 최종 매출원가·공급단가는 혼합·제조·검사·포장·수율손실·물류·거래조건을 반영한 유효 견적서로 확정합니다.</p></div></section>'''


def patch_index_html(text: str, cfg: dict[str, Any]) -> str:
    pattern = re.compile(r'<section class="brand-evolution" id="caremix-dose".*?</section>', re.DOTALL)
    replacement = caremix_section(cfg)
    if not pattern.search(text):
        raise ValueError("caremix-dose section not found in docs/index.html")
    return pattern.sub(replacement, text, count=1)


def patch_technical_documents(data: dict[str, Any], cfg: dict[str, Any]) -> bool:
    changed = False
    data["updated_at"] = cfg["effective_date"]
    for item in data.get("items", []):
        if item.get("id") != "caremix-spec":
            continue
        desired = {
            "version": "1.1",
            "status": "NEW",
            "description": "GABA 10% 설계, 사료 1톤당 1kg 적용, 가바크루드 18,000원/kg 기준의 원료비 10,500원/kg 산술과 최종 견적 구분",
        }
        for key, value in desired.items():
            if item.get(key) != value:
                item[key] = value
                changed = True
    return changed


def validate(cfg: dict[str, Any]) -> None:
    crude = cfg["gaba_crude"]["public_supply_price_krw_per_kg"]
    mineral = cfg["mineral_matrix"]["price_krw_per_kg"]
    cf = cfg["care_mix"]["gaba_crude_fraction"]
    mf = cfg["care_mix"]["mineral_matrix_fraction"]
    expected = round(crude * cf + mineral * mf)
    configured = cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"]
    if abs(cf + mf - 1.0) > 1e-9:
        raise ValueError("Care Mix fractions must sum to 1")
    if expected != configured:
        raise ValueError(f"Care Mix cost mismatch: expected {expected}, configured {configured}")
    gaba = cfg["gaba_crude"]["gaba_fraction"] * cf
    if abs(gaba - cfg["care_mix"]["gaba_fraction"]) > 1e-9:
        raise ValueError("Care Mix GABA fraction mismatch")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    cfg = load_json(CONFIG_PATH)
    validate(cfg)
    changed_paths: list[str] = []

    for path in SOURCE_JSONS:
        data = load_json(path)
        before = json.dumps(data, ensure_ascii=False, sort_keys=True)
        reconcile_assumptions(data, cfg)
        after = json.dumps(data, ensure_ascii=False, sort_keys=True)
        if before != after:
            if not args.check:
                dump_json(path, data)
            changed_paths.append(str(path.relative_to(ROOT)))

    public_payload = dict(cfg)
    public_payload["calculation_check"] = {
        "gaba_crude_component_krw": int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"] * cfg["care_mix"]["gaba_crude_fraction"]),
        "mineral_component_krw": int(cfg["mineral_matrix"]["price_krw_per_kg"] * cfg["care_mix"]["mineral_matrix_fraction"]),
        "total_krw_per_kg": cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"],
    }
    public_text = json.dumps(public_payload, ensure_ascii=False, indent=2) + "\n"
    current_public = PUBLIC_PRICING.read_text(encoding="utf-8") if PUBLIC_PRICING.exists() else ""
    if current_public != public_text:
        if not args.check:
            PUBLIC_PRICING.parent.mkdir(parents=True, exist_ok=True)
            PUBLIC_PRICING.write_text(public_text, encoding="utf-8")
        changed_paths.append(str(PUBLIC_PRICING.relative_to(ROOT)))

    html = INDEX_HTML.read_text(encoding="utf-8")
    patched_html = patch_index_html(html, cfg)
    if patched_html != html:
        if not args.check:
            INDEX_HTML.write_text(patched_html, encoding="utf-8")
        changed_paths.append(str(INDEX_HTML.relative_to(ROOT)))

    tech = load_json(TECH_DOCS)
    before_tech = json.dumps(tech, ensure_ascii=False, sort_keys=True)
    patch_technical_documents(tech, cfg)
    after_tech = json.dumps(tech, ensure_ascii=False, sort_keys=True)
    if before_tech != after_tech:
        if not args.check:
            dump_json(TECH_DOCS, tech)
        changed_paths.append(str(TECH_DOCS.relative_to(ROOT)))

    stale_text = [
        "0.5kg×7,000원",
        "가바크루드 50% + 미네랄매트릭스 50% · 5,000원/kg",
        "가바크루드 표준품 원가\",\n      \"value\": \"7,000원/kg",
        "내부 제조 시 원가 하한 참고",
    ]
    for path in [*SOURCE_JSONS, INDEX_HTML]:
        text = (patched_html if path == INDEX_HTML else (json.dumps(load_json(path), ensure_ascii=False) if path.exists() else ""))
        found = [needle for needle in stale_text if needle in text]
        if found and not args.check:
            raise ValueError(f"stale pricing remains in {path}: {found}")

    if args.check and changed_paths:
        raise SystemExit("pricing reconciliation required: " + ", ".join(changed_paths))
    print(json.dumps({"changed": changed_paths, "caremix_raw_material_cost": cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
