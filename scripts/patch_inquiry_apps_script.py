#!/usr/bin/env python3
"""Idempotently install the Apps Script inquiry receiver client."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
SCRIPT_TAG = '<script src="assets/inquiry-apps-script.js" defer data-inquiry-apps-script="v1"></script>'
DELIVERY_SCRIPT = '<script src="assets/inquiry-delivery-fix.js" defer data-inquiry-delivery="v1"></script>'
INQUIRY_SCRIPT = '<script src="assets/inquiry-form.js" defer data-inquiry-form="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    if SCRIPT_TAG in text:
        return text, False
    if DELIVERY_SCRIPT in text:
        return text.replace(DELIVERY_SCRIPT, DELIVERY_SCRIPT + SCRIPT_TAG, 1), True
    if INQUIRY_SCRIPT in text:
        return text.replace(INQUIRY_SCRIPT, INQUIRY_SCRIPT + SCRIPT_TAG, 1), True
    if "</body>" in text:
        return text.replace("</body>", SCRIPT_TAG + "\n</body>", 1), True
    raise RuntimeError("docs/index.html is missing a script insertion point")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = TARGET.read_text(encoding="utf-8")
    patched, changed = patch_text(text)
    if args.check:
        if changed:
            raise SystemExit("Apps Script inquiry client is not installed")
        print("Apps Script inquiry client installed")
        return 0
    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed Apps Script inquiry client")
    else:
        print("Apps Script inquiry client already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
