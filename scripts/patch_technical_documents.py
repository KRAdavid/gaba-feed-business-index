#!/usr/bin/env python3
"""Install technical-business material center assets in docs/index.html."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/technical-documents.css" data-technical-documents="v1">'
SCRIPT_TAG = '<script src="assets/technical-documents.js" defer data-technical-documents="v1"></script>'
SPLIT_STYLE = '<link rel="stylesheet" href="assets/product-split-selector.css" data-product-split-selector="v1">'
SPLIT_SCRIPT = '<script src="assets/product-split-selector.js" defer data-product-split-selector="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False
    if STYLE_TAG not in text:
        if SPLIT_STYLE in text:
            text = text.replace(SPLIT_STYLE, SPLIT_STYLE + "\n" + STYLE_TAG, 1)
        elif "</head>" in text:
            text = text.replace("</head>", STYLE_TAG + "\n</head>", 1)
        else:
            raise RuntimeError("docs/index.html is missing </head>")
        changed = True
    if SCRIPT_TAG not in text:
        if SPLIT_SCRIPT in text:
            text = text.replace(SPLIT_SCRIPT, SPLIT_SCRIPT + SCRIPT_TAG, 1)
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
            raise SystemExit("technical document center assets are not installed")
        print("technical document center assets installed")
        return 0
    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed technical document center assets")
    else:
        print("technical document center assets already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
