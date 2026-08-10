#!/usr/bin/env python3
"""Validate the product SOT and its public static snapshot."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MASTER = ROOT / "data" / "product_master.json"
PUBLIC = ROOT / "docs" / "data" / "products.json"
REQUIRED = {
    "product_id", "product_name", "version", "gaba_content", "specification_status",
    "carrier", "moisture", "appearance", "analytical_method", "recommended_inclusion",
    "dose_basis", "moq", "packing", "lead_time", "price_status", "coa_status",
    "regulatory_status", "last_updated", "approved_by",
}
ALLOWED_UNKNOWN = {"TBD", "Pending Verification", "Pilot Assumption", ""}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def validate() -> list[str]:
    errors: list[str] = []
    master = load(MASTER)
    public = load(PUBLIC)
    if master != public:
        errors.append("public product snapshot does not match product master")
    products = master.get("products", [])
    if {p.get("product_id") for p in products} != {"GABA-CRUDE-20", "GABA-CARE-MIX"}:
        errors.append("product master must contain exactly the two approved product IDs")
    if master.get("dose_basis") != "mg active GABA / kg complete feed":
        errors.append("product master dose basis is not standardized")
    for product in products:
        missing = REQUIRED - set(product)
        if missing:
            errors.append(f"{product.get('product_id')}: missing {sorted(missing)}")
        for key, value in product.items():
            if key.endswith("_status") and value not in ALLOWED_UNKNOWN:
                continue
            if value is None:
                errors.append(f"{product.get('product_id')}: null value in {key}")
    return errors


if __name__ == "__main__":
    problems = validate()
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}")
        raise SystemExit(1)
    print(json.dumps({"ok": True, "products": 2}))
