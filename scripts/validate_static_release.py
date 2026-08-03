#!/usr/bin/env python3
"""Validate the host-independent static deployment folder and ZIP archive."""

from __future__ import annotations

import hashlib
import json
import re
import zipfile
from pathlib import Path, PurePosixPath


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "release" / "GABA_Feed_Public_Site_Static"
ARCHIVE = ROOT / "release" / "GABA_Feed_Public_Site_Static_Deploy.zip"
MAX_DIRECT_UPLOAD_FILE_BYTES = 25 * 1024 * 1024
REQUIRED = {
    "index.html",
    "404.html",
    "assets/app.js",
    "assets/styles.css",
    "data/index.json",
    "health.json",
    "release-manifest.json",
    "DEPLOYMENT_GUIDE.md",
    "downloads/GABA_Feed_Business_Model_Speech_Deck_v1.pdf",
    "downloads/GABA_Crude_Specification.md",
    "downloads/GABA_Caremix_Specification.md",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate() -> list[str]:
    errors: list[str] = []
    if not OUTPUT.is_dir():
        return ["static release folder is missing"]
    if not ARCHIVE.is_file():
        return ["static release ZIP is missing"]

    actual = {path.relative_to(OUTPUT).as_posix() for path in OUTPUT.rglob("*") if path.is_file()}
    for missing in sorted(REQUIRED - actual):
        errors.append(f"required static release file is missing: {missing}")
    if any(path == ".openai/hosting.json" or path.startswith(".openai/") for path in actual):
        errors.append("Sites-specific .openai configuration is present")

    index_html = (OUTPUT / "index.html").read_text(encoding="utf-8")
    if 'rel="canonical"' in index_html or 'property="og:url"' in index_html:
        errors.append("domain-specific canonical metadata remains in the portable release")
    public_text = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in OUTPUT.rglob("*")
        if path.is_file() and path.suffix.lower() in {".html", ".js", ".css", ".json", ".md", ".txt"}
    )
    if re.search(r"[A-Za-z]:\\(?:Users|Documents|Downloads)\\", public_text):
        errors.append("release contains a local Windows path")
    if "appgprj_" in public_text:
        errors.append("release contains a Sites project identifier")

    manifest_path = OUTPUT / "release-manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest.get("deployment_mode") != "static-host-independent":
            errors.append("deployment mode is not host-independent")
        listed = {row["path"]: row for row in manifest.get("files", [])}
        for path, row in listed.items():
            target = OUTPUT / path
            if not target.is_file():
                errors.append(f"manifest file is missing: {path}")
            elif sha256(target) != row.get("sha256"):
                errors.append(f"manifest checksum differs: {path}")

    with zipfile.ZipFile(ARCHIVE) as archive:
        names = archive.namelist()
        if "index.html" not in names:
            errors.append("ZIP does not have index.html at its root")
        if set(names) != actual:
            errors.append("ZIP contents differ from the static release folder")
        for info in archive.infolist():
            path = PurePosixPath(info.filename)
            if path.is_absolute() or ".." in path.parts:
                errors.append(f"unsafe ZIP path: {info.filename}")
            if info.file_size > MAX_DIRECT_UPLOAD_FILE_BYTES:
                errors.append(f"file exceeds 25 MiB direct-upload limit: {info.filename}")

    for source_name in (
        "GABA_Feed_Business_Model_Speech_Deck_v1.pdf",
        "GABA_Crude_Specification.md",
        "GABA_Caremix_Specification.md",
    ):
        source = ROOT / source_name
        deployed = OUTPUT / "downloads" / source_name
        if not source.is_file() or not deployed.is_file() or sha256(source) != sha256(deployed):
            errors.append(f"download is not synchronized: {source_name}")
    return errors


def main() -> None:
    errors = validate()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    health = json.loads((OUTPUT / "health.json").read_text(encoding="utf-8"))
    print(
        json.dumps(
            {
                "ok": True,
                "mode": health["deployment_mode"],
                "version": health["version"],
                "files": len([p for p in OUTPUT.rglob("*") if p.is_file()]),
                "archive_bytes": ARCHIVE.stat().st_size,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
