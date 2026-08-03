#!/usr/bin/env python3
"""Copy the reviewed working files into the public download directory."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
FILES = {
    "GABA_Feed_Business_Model_Speech_Deck_v1.pptx": "GABA_Feed_Business_Model_Speech_Deck_v1.pptx",
    "GABA_Crude_Specification.md": "GABA_Crude_Specification.md",
    "GABA_Caremix_Specification.md": "GABA_Caremix_Specification.md",
}


def main() -> None:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    # Keep the public download surface intentionally limited to the approved three files.
    for stale_name in ("GABA_Index_Master.xlsx", "GABA_Index_운영가이드.md"):
        stale = DOWNLOADS / stale_name
        if stale.exists():
            stale.unlink()
    for source_name, target_name in FILES.items():
        source = ROOT / source_name
        if not source.exists():
            raise FileNotFoundError(f"required public download is missing: {source}")
        shutil.copy2(source, DOWNLOADS / target_name)
    print(f"prepared {len(FILES)} downloads in {DOWNLOADS}")


if __name__ == "__main__":
    main()
