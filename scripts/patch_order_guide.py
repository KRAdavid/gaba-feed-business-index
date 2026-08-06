#!/usr/bin/env python3
"""Idempotently install product order guide assets in docs/index.html."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/order-guide.css" data-order-guide="v1">'
SCRIPT_TAG = '<script src="assets/order-guide.js" defer data-order-guide="v1"></script>'
INQUIRY_SCRIPT = '<script src="assets/inquiry-form.js" defer data-inquiry-form="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False
    if STYLE_TAG not in text:
        if "</head>" not in text:
            raise RuntimeError("docs/index.html is missing </head>")
        text = text.replace("</head>", f"{STYLE_TAG}\n</head>", 1)
        changed = True

    if SCRIPT_TAG not in text:
        if INQUIRY_SCRIPT in text:
            text = text.replace(INQUIRY_SCRIPT, f"{INQUIRY_SCRIPT}{SCRIPT_TAG}", 1)
        elif "</body>" in text:
            text = text.replace("</body>", f"{SCRIPT_TAG}\n</body>", 1)
        else:
            raise RuntimeError("docs/index.html is missing </body>")
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
            raise SystemExit("order guide asset references are not installed")
        print("order guide asset references installed")
        return 0
    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed product order guide asset references")
    else:
        print("product order guide asset references already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
