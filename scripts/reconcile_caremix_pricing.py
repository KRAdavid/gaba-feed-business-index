#!/usr/bin/env python3
"""Reconcile every public Care Mix price with the approved 2026-08-10 basis.

Authoritative arithmetic:
- GABA Crude 20: 18,000 KRW/kg
- Mineral Matrix: 5,000 KRW/kg
- Mix: 50:50
- Theoretical raw-material cost: 11,500 KRW/kg
- Application: 1 kg Care Mix/feed ton -> 11,500 KRW/feed ton

The 11,500 KRW figure is not final COGS or a customer supply price. Manufacturing,
quality testing, packaging, yield loss, logistics, taxes and transaction terms remain
outside the raw-material arithmetic and require a valid quotation.
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


def krw_per_kg(value: int) -> str:
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


def validate(cfg: dict[str, Any]) -> None:
    crude = int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"])
    mineral = int(cfg["mineral_matrix"]["price_krw_per_kg"])
    crude_fraction = float(cfg["care_mix"]["gaba_crude_fraction"])
    mineral_fraction = float(cfg["care_mix"]["mineral_matrix_fraction"])
    configured = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"])
    feed_ton = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_feed_ton"])

    if crude != 18000:
        raise ValueError(f"GABA Crude public basis must be 18,000 KRW/kg, got {crude}")
    if mineral != 5000:
        raise ValueError(f"Mineral Matrix public basis must be 5,000 KRW/kg, got {mineral}")
    if abs(crude_fraction + mineral_fraction - 1.0) > 1e-9:
        raise ValueError("Care Mix fractions must sum to 1")

    expected = round(crude * crude_fraction + mineral * mineral_fraction)
    if expected != configured or expected != 11500:
        raise ValueError(f"Care Mix cost mismatch: expected 11,500, configured {configured}")
    if feed_ton != expected:
        raise ValueError("Care Mix feed-ton raw-material cost must equal 11,500 at 1 kg/t")

    gaba_fraction = float(cfg["gaba_crude"]["gaba_fraction"]) * crude_fraction
    if abs(gaba_fraction - float(cfg["care_mix"]["gaba_fraction"])) > 1e-9:
        raise ValueError("Care Mix GABA fraction mismatch")
    final_mg = gaba_fraction * float(cfg["care_mix"]["application_kg_per_feed_ton"]) * 1_000_000 / 1000
    if abs(final_mg - float(cfg["care_mix"]["nominal_final_gaba_mg_per_kg"])) > 1e-9:
        raise ValueError("Final-feed nominal GABA concentration mismatch")


def reconcile_assumptions(data: dict[str, Any], cfg: dict[str, Any]) -> None:
    rows = assumptions_of(data)

    # Do not expose obsolete internal proxies as current customer-facing prices.
    rows[:] = [row for row in rows if row.get("metric") not in {
        "가바크루드 표준품 원가",
        "내부 제조 시 원가 하한 참고",
    }]

    crude = int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"])
    mineral = int(cfg["mineral_matrix"]["price_krw_per_kg"])
    caremix = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"])
    crude_component = int(cfg["care_mix"]["gaba_crude_component_krw_per_kg"])
    mineral_component = int(cfg["care_mix"]["mineral_matrix_component_krw_per_kg"])

    replace_or_append(rows, "가바크루드 판매가격", {
        "metric": "가바크루드 판매가격",
        "value": krw_per_kg(crude),
        "state": "사용자 확정 공개 기준",
        "formula": "Care Mix 공개 산술에 적용; VAT·운송·고객별 거래조건 별도",
        "unlock": "고객별 유효 견적서와 거래조건",
    })
    replace_or_append(rows, "미네랄매트릭스 기준가격", {
        "metric": "미네랄매트릭스 기준가격",
        "value": krw_per_kg(mineral),
        "state": "사용자 확정 공개 기준",
        "formula": "Care Mix 50% 배합 산술에 적용; VAT·운송·고객별 거래조건 별도",
        "unlock": "실제 구매·공급 견적서와 거래조건",
    })
    replace_or_append(rows, "가바케어믹스 혼합비·원료 투입원가", {
        "metric": "가바케어믹스 혼합비·원료 투입원가",
        "value": f"가바크루드 50% + 미네랄매트릭스 50% · {caremix:,}원/kg",
        "state": "사용자 확정 기준가의 이론 계산",
        "formula": (
            f"GABA 20% 가바크루드 0.5kg×{crude:,}원/kg = {crude_component:,}원 + "
            f"미네랄매트릭스 0.5kg×{mineral:,}원/kg = {mineral_component:,}원; "
            f"합계 {caremix:,}원/kg, 사료 1톤당 {caremix:,}원"
        ),
        "unlock": "혼합·제조·검사·포장·수율손실·물류·고객별 거래조건 확인",
    })
    replace_or_append(rows, "가바케어믹스 최종 매출원가·공급단가", {
        "metric": "가바케어믹스 최종 매출원가·공급단가",
        "value": "시험생산·견적 후 확정",
        "state": "계산 대기",
        "formula": f"원료 투입 이론값 {caremix:,}원/kg + 혼합·제조·검사·포장·수율손실·물류·거래조건",
        "unlock": "OEM 견적·시험생산 실수율·검사·포장·물류비와 고객별 공급조건",
    })

    data["pricing_reference"] = cfg


def caremix_section(cfg: dict[str, Any]) -> str:
    crude = int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"])
    mineral = int(cfg["mineral_matrix"]["price_krw_per_kg"])
    total = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"])
    crude_component = int(cfg["care_mix"]["gaba_crude_component_krw_per_kg"])
    mineral_component = int(cfg["care_mix"]["mineral_matrix_component_krw_per_kg"])
    return f'''<section class="brand-evolution" id="caremix-dose" data-pricing-version="1.2" data-pricing-date="{cfg['effective_date']}"><div class="container"><div class="section-title left"><span class="product-label">PRICING BASIS v1.2 · {cfg['effective_date']}</span><h2>가바케어믹스는 사료 1톤당 1kg 투입 기준으로 설계합니다</h2><p>최종 사료의 명목 GABA 100mg/kg 기준을 충족하도록 GABA 20% 가바크루드와 미네랄매트릭스를 50:50으로 배합합니다.</p></div><div class="evolution-grid"><article class="evolution-step"><span>투입 기준</span><h3>사료 1톤당 1kg</h3><p>Care Mix 1kg을 사료 1톤에 투입하는 제품 설계 기준입니다.</p></article><article class="evolution-step"><span>최종 사료 설계</span><h3>GABA 100mg/kg</h3><p>가바크루드 0.5kg에 포함된 GABA 100g을 사료 1톤에 공급하는 명목 기준입니다.</p></article><article class="evolution-step"><span>혼합비</span><h3>가바크루드 50%<br>미네랄매트릭스 50%</h3><p>가바크루드 0.5kg + 미네랄매트릭스 0.5kg으로 Care Mix GABA 10%를 설계합니다.</p></article><article class="evolution-step final"><span>원료 투입 이론값</span><h3>{total:,}원/kg</h3><p>가바크루드 {crude_component:,}원 + 미네랄매트릭스 {mineral_component:,}원. 사료 1톤당 {total:,}원입니다.</p></article></div><div class="model-columns" style="margin-top:18px"><div><h3>가바크루드 원료분</h3><p>0.5kg × {crude:,}원/kg = <strong>{crude_component:,}원</strong></p></div><div><h3>미네랄매트릭스 원료분</h3><p>0.5kg × {mineral:,}원/kg = <strong>{mineral_component:,}원</strong></p></div></div><p class="story-disclaimer"><strong>가격 구분:</strong> {total:,}원/kg은 원료 2종만 반영한 이론 원료비이며 가바케어믹스의 최종 매출원가 또는 판매가격이 아닙니다. 가바크루드와 미네랄매트릭스 기준가는 각각 {crude:,}원/kg, {mineral:,}원/kg이며 VAT·운송·거래조건은 별도입니다. 최종 공급단가는 혼합·제조·검사·포장·수율손실·물류·거래조건을 반영한 유효 견적서로 확정합니다.</p></div></section>'''


def patch_index_html(text: str, cfg: dict[str, Any]) -> str:
    pattern = re.compile(r'<section class="brand-evolution" id="caremix-dose".*?</section>', re.DOTALL)
    if not pattern.search(text):
        raise ValueError("caremix-dose section not found in docs/index.html")
    return pattern.sub(caremix_section(cfg), text, count=1)


def patch_technical_documents(data: dict[str, Any], cfg: dict[str, Any]) -> None:
    data["updated_at"] = cfg["effective_date"]
    for item in data.get("items", []):
        if item.get("id") != "caremix-spec":
            continue
        item.update({
            "version": "1.2",
            "status": "NEW",
            "description": "GABA 10% 설계, 사료 1톤당 1kg 적용, 가바크루드 18,000원/kg·미네랄매트릭스 5,000원/kg 기준의 이론 원료비 11,500원/kg 산술과 최종 견적 구분",
        })


def patch_known_text(text: str) -> str:
    replacements = {
        "가바크루드 0.5kg×7,000원/kg + 미네랄매트릭스 0.5kg×3,000원/kg = 5,000원/kg": "가바크루드 0.5kg×18,000원/kg + 미네랄매트릭스 0.5kg×5,000원/kg = 11,500원/kg",
        "가바크루드 50% + 미네랄매트릭스 50% · 5,000원/kg": "가바크루드 50% + 미네랄매트릭스 50% · 11,500원/kg",
        "0.5kg×18,000원/kg + 0.5kg×3,000원/kg = 10,500원/kg": "0.5kg×18,000원/kg + 0.5kg×5,000원/kg = 11,500원/kg",
        "미네랄매트릭스 3,000원/kg": "미네랄매트릭스 5,000원/kg",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


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
        "gaba_crude_component_krw": int(cfg["care_mix"]["gaba_crude_component_krw_per_kg"]),
        "mineral_component_krw": int(cfg["care_mix"]["mineral_matrix_component_krw_per_kg"]),
        "total_krw_per_kg": int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"]),
        "total_krw_per_feed_ton": int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_feed_ton"]),
    }
    public_text = json.dumps(public_payload, ensure_ascii=False, indent=2) + "\n"
    current_public = PUBLIC_PRICING.read_text(encoding="utf-8") if PUBLIC_PRICING.exists() else ""
    if current_public != public_text:
        if not args.check:
            PUBLIC_PRICING.parent.mkdir(parents=True, exist_ok=True)
            PUBLIC_PRICING.write_text(public_text, encoding="utf-8")
        changed_paths.append(str(PUBLIC_PRICING.relative_to(ROOT)))

    html = INDEX_HTML.read_text(encoding="utf-8")
    patched_html = patch_known_text(patch_index_html(html, cfg))
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

    # Apply only exact known corrections in other public UTF-8 materials.
    for folder in (ROOT / "docs" / "materials",):
        if not folder.exists():
            continue
        for path in folder.rglob("*.html"):
            original = path.read_text(encoding="utf-8")
            patched = patch_known_text(original)
            if patched != original:
                if not args.check:
                    path.write_text(patched, encoding="utf-8")
                changed_paths.append(str(path.relative_to(ROOT)))

    stale_patterns = [
        re.compile(r"미네랄매트릭스[^\n<]{0,120}3,000원/kg"),
        re.compile(r"0\.5kg\s*[×xX*]\s*18,000원/kg\s*\+\s*0\.5kg\s*[×xX*]\s*3,000원/kg"),
        re.compile(r"가바케어믹스[^\n<]{0,160}10,500원/kg"),
        re.compile(r"가바크루드 50%\s*\+\s*미네랄매트릭스 50%[^\n<]{0,80}5,000원/kg"),
    ]
    check_paths = [*SOURCE_JSONS, PUBLIC_PRICING, TECH_DOCS, INDEX_HTML]
    check_paths += list((ROOT / "docs" / "materials").glob("*.html")) if (ROOT / "docs" / "materials").exists() else []
    stale_hits: list[str] = []
    for path in check_paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for pattern in stale_patterns:
            if pattern.search(text):
                stale_hits.append(f"{path.relative_to(ROOT)} :: {pattern.pattern}")
    if stale_hits:
        raise ValueError("stale Care Mix pricing remains:\n" + "\n".join(stale_hits))

    if args.check and changed_paths:
        raise SystemExit("pricing reconciliation required: " + ", ".join(changed_paths))

    print(json.dumps({
        "changed": sorted(set(changed_paths)),
        "gaba_crude_price": cfg["gaba_crude"]["public_supply_price_krw_per_kg"],
        "mineral_matrix_price": cfg["mineral_matrix"]["price_krw_per_kg"],
        "caremix_raw_material_cost": cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"],
        "caremix_feed_ton_cost": cfg["care_mix"]["calculated_raw_material_cost_krw_per_feed_ton"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
