#!/usr/bin/env python3
"""Idempotently install rotating hero-banner assets in docs/index.html."""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "docs" / "index.html"
STYLE_TAG = '<link rel="stylesheet" href="assets/hero-banner-rotator.css" data-hero-banner-rotator="v1">'
SCRIPT_TAG = '<script src="assets/hero-banner-rotator.js" defer data-hero-banner-rotator="v1"></script>'
STYLE_ANCHOR = '<link rel="stylesheet" href="assets/cta-emphasis.css" data-cta-emphasis="v1">'
SCRIPT_ANCHOR = '<script src="assets/cta-emphasis.js" defer data-cta-emphasis="v1"></script>'


def patch_text(text: str) -> tuple[str, bool]:
    changed = False

    if STYLE_TAG not in text:
        if STYLE_ANCHOR in text:
            text = text.replace(STYLE_ANCHOR, STYLE_ANCHOR + "\n" + STYLE_TAG, 1)
        elif "</head>" in text:
            text = text.replace("</head>", STYLE_TAG + "\n</head>", 1)
        else:
            raise RuntimeError("docs/index.html is missing </head>")
        changed = True

    if SCRIPT_TAG not in text:
        if SCRIPT_ANCHOR in text:
            text = text.replace(SCRIPT_ANCHOR, SCRIPT_ANCHOR + SCRIPT_TAG, 1)
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
            raise SystemExit("rotating hero-banner assets are not installed")
        print("rotating hero-banner assets installed")
        return 0

    if changed:
        TARGET.write_text(patched, encoding="utf-8")
        print("installed rotating hero-banner assets")
    else:
        print("rotating hero-banner assets already installed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
