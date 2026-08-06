#!/usr/bin/env python3
"""Idempotently install visitor decision-card assets in docs/index.html."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/visitor-decision-cards.css" data-visitor-decision="v1">'
SCRIPT_TAG = '<script src="assets/visitor-decision-cards.js" defer data-visitor-decision="v1"></script>'
ORDER_STYLE = '<link rel="stylesheet" href="assets/order-guide.css" data-order-guide="v1">'
ORDER_SCRIPT = '<script src="assets/order-guide.js" defer data-order-guide="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if STYLE_TAG not in text:
        if ORDER_STYLE in text:
            text = text.replace(ORDER_STYLE, ORDER_STYLE + "\n" + STYLE_TAG, 1)
        elif "</head>" in text:
            text = text.replace("</head>", STYLE_TAG + "\n</head>", 1)
        else:
            raise RuntimeError("docs/index.html is missing </head>")
        changed = True

    if SCRIPT_TAG not in text:
        if ORDER_SCRIPT in text:
            text = text.replace(ORDER_SCRIPT, ORDER_SCRIPT + SCRIPT_TAG, 1)
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
            raise SystemExit("visitor decision-card assets are not installed")
        print("visitor decision-card assets installed")
        return 0

    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed visitor decision-card assets")
    else:
        print("visitor decision-card assets already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
