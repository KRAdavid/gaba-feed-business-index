#!/usr/bin/env python3
"""Replace the legacy GABA Feed inquiry mailbox in live source files."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OLD = "dubaissday" + "@cellpinda.com"
NEW = "feed@cellpinda.com"

TARGETS = [
    "apps-script/Inquiry.gs",
    "apps-script/Inquiry_v2.gs",
    "docs/assets/inquiry-form.js",
    "docs/assets/inquiry-apps-script.js",
    "docs/assets/inquiry-delivery-fix.js",
    "APPS_SCRIPT_INQUIRY_SETUP.md",
    ".github/workflows/install-inquiry-delivery.yml",
]


def main() -> int:
    changed: list[str] = []
    missing: list[str] = []

    for relative in TARGETS:
        path = ROOT / relative
        if not path.exists():
            missing.append(relative)
            continue
        text = path.read_text(encoding="utf-8")
        replaced = text.replace(OLD, NEW)
        if replaced != text:
            path.write_text(replaced, encoding="utf-8")
            changed.append(relative)

    print(f"recipient: {NEW}")
    print(f"changed: {len(changed)}")
    for item in changed:
        print(f"  - {item}")
    if missing:
        print("missing optional targets:")
        for item in missing:
            print(f"  - {item}")

    required = [
        ROOT / "apps-script/Inquiry_v2.gs",
        ROOT / "docs/assets/inquiry-form.js",
        ROOT / "docs/assets/inquiry-apps-script.js",
    ]
    for path in required:
        text = path.read_text(encoding="utf-8")
        if OLD in text:
            raise SystemExit(f"legacy recipient remains in {path.relative_to(ROOT)}")
        if NEW not in text:
            raise SystemExit(f"new recipient missing from {path.relative_to(ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
