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
    changed = False

    # FormSubmit is retired. Leaving its capture-phase listener installed can
    # overwrite the Apps Script action immediately before a valid submission.
    if DELIVERY_SCRIPT in text:
        text = text.replace(DELIVERY_SCRIPT, "", 1)
        changed = True

    if SCRIPT_TAG not in text:
        if INQUIRY_SCRIPT in text:
            text = text.replace(INQUIRY_SCRIPT, INQUIRY_SCRIPT + SCRIPT_TAG, 1)
        elif "</body>" in text:
            text = text.replace("</body>", SCRIPT_TAG + "\n</body>", 1)
        else:
            raise RuntimeError("docs/index.html is missing a script insertion point")
        changed = True

    return text, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    text = TARGET.read_text(encoding="utf-8")
    patched, changed = patch_text(text)
    if args.check:
        if changed:
            raise SystemExit("Apps Script inquiry client is not cleanly installed")
        if DELIVERY_SCRIPT in text:
            raise SystemExit("obsolete FormSubmit runtime is still installed")
        print("Apps Script inquiry client installed; FormSubmit runtime removed")
        return 0
    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed Apps Script inquiry client and removed FormSubmit runtime")
    else:
        print("Apps Script inquiry client already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
