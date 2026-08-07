#!/usr/bin/env python3
"""Idempotently install the Cellpinda Life Science Lab section assets."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/lab-section.css" data-lab-section="v1">'
SCRIPT_TAG = '<script src="assets/lab-section.js" defer data-lab-section="v1"></script>'
PRODUCT_STYLE = '<link rel="stylesheet" href="assets/product-split-selector.css" data-product-split-selector="v1">'
PRODUCT_SCRIPT = '<script src="assets/product-split-selector.js" defer data-product-split-selector="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if STYLE_TAG not in text:
        if PRODUCT_STYLE in text:
            text = text.replace(PRODUCT_STYLE, PRODUCT_STYLE + "\n" + STYLE_TAG, 1)
        elif "</head>" in text:
            text = text.replace("</head>", STYLE_TAG + "\n</head>", 1)
        else:
            raise RuntimeError("docs/index.html is missing </head>")
        changed = True

    if SCRIPT_TAG not in text:
        if PRODUCT_SCRIPT in text:
            text = text.replace(PRODUCT_SCRIPT, PRODUCT_SCRIPT + SCRIPT_TAG, 1)
        elif "</body>" in text:
            text = text.replace("</body>", SCRIPT_TAG + "\n</body>", 1)
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
            raise SystemExit("Life Science Lab assets are not installed")
        print("Life Science Lab assets installed")
        return 0

    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed Life Science Lab assets")
    else:
        print("Life Science Lab assets already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
