#!/usr/bin/env python3
"""Idempotently install selectable growth/FCR calculator scenario assets."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/calculator-scenarios.css" data-calculator-scenarios="v1">'
SCRIPT_TAG = '<script src="assets/calculator-scenarios.js" defer data-calculator-scenarios="v1"></script>'
INQUIRY_SCRIPT = '<script src="assets/inquiry-form.js" defer data-inquiry-form="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if STYLE_TAG not in text:
        if "</head>" not in text:
            raise RuntimeError("docs/index.html is missing </head>")
        text = text.replace("</head>", STYLE_TAG + "\n</head>", 1)
        changed = True

    if SCRIPT_TAG not in text:
        if INQUIRY_SCRIPT in text:
            text = text.replace(INQUIRY_SCRIPT, SCRIPT_TAG + INQUIRY_SCRIPT, 1)
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
            raise SystemExit("selectable calculator scenario assets are not installed")
        print("selectable calculator scenario assets installed")
        return 0

    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed selectable calculator scenario assets")
    else:
        print("selectable calculator scenario assets already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
