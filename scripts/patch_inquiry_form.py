#!/usr/bin/env python3
"""Idempotently load the business inquiry form assets on the public dashboard."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/inquiry-form.css" data-inquiry-form="v1">'
SCRIPT_TAG = '<script src="assets/inquiry-form.js" defer data-inquiry-form="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if STYLE_TAG not in text:
        if "</head>" not in text:
            raise RuntimeError("docs/index.html has no closing </head> tag")
        text = text.replace("</head>", f"{STYLE_TAG}\n</head>", 1)
        changed = True

    if SCRIPT_TAG not in text:
        if "</body>" not in text:
            raise RuntimeError("docs/index.html has no closing </body> tag")
        text = text.replace("</body>", f"{SCRIPT_TAG}\n</body>", 1)
        changed = True

    return text, changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    original = TARGET.read_text(encoding="utf-8")
    patched, changed = patch_text(original)

    if args.check:
        if changed:
            raise SystemExit("inquiry form asset tags are not installed")
        print("inquiry form asset tags are installed")
        return 0

    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed inquiry form asset tags in docs/index.html")
    else:
        print("docs/index.html already loads inquiry form assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
