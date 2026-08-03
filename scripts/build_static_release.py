#!/usr/bin/env python3
"""Build a host-independent static deployment bundle from the reviewed site."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
STATIC_EXTRAS = ROOT / "deploy" / "static"
RELEASE_ROOT = ROOT / "release"
OUTPUT = RELEASE_ROOT / "GABA_Feed_Public_Site_Static"
ARCHIVE = RELEASE_ROOT / "GABA_Feed_Public_Site_Static_Deploy.zip"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git_revision() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short=12", "HEAD"],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unversioned"


def reset_output() -> None:
    RELEASE_ROOT.mkdir(parents=True, exist_ok=True)
    resolved_root = RELEASE_ROOT.resolve()
    resolved_output = OUTPUT.resolve()
    if resolved_output.parent != resolved_root or resolved_output.name != "GABA_Feed_Public_Site_Static":
        raise RuntimeError(f"refusing to clear unexpected release path: {resolved_output}")
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    if ARCHIVE.exists():
        ARCHIVE.unlink()


def make_domain_neutral() -> None:
    index_path = OUTPUT / "index.html"
    html = index_path.read_text(encoding="utf-8")
    html = re.sub(r'\s*<meta property="og:url"[^>]*>', "", html, count=1)
    html = re.sub(r'\s*<link rel="canonical"[^>]*>', "", html, count=1)
    index_path.write_text(html, encoding="utf-8", newline="\n")


def write_release_metadata() -> dict[str, str]:
    data = json.loads((OUTPUT / "data" / "index.json").read_text(encoding="utf-8"))
    metadata = {
        "status": "ok",
        "service": "gaba-feed-business-index",
        "deployment_mode": "static-host-independent",
        "version": git_revision(),
        "built_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "snapshot_generated_at": data["meta"]["generated_at"],
    }
    (OUTPUT / "health.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return metadata


def write_manifest(metadata: dict[str, str]) -> None:
    files = []
    for path in sorted(OUTPUT.rglob("*")):
        if path.is_file() and path.name != "release-manifest.json":
            files.append(
                {
                    "path": path.relative_to(OUTPUT).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path),
                }
            )
    manifest = {
        **metadata,
        "entrypoint": "index.html",
        "file_count": len(files),
        "files": files,
    }
    (OUTPUT / "release-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def write_archive() -> None:
    with zipfile.ZipFile(ARCHIVE, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in sorted(OUTPUT.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(OUTPUT).as_posix())


def main() -> None:
    required = (DOCS / "index.html", DOCS / "data" / "index.json", STATIC_EXTRAS / "DEPLOYMENT_GUIDE.md")
    for path in required:
        if not path.exists():
            raise FileNotFoundError(f"required release input is missing: {path.relative_to(ROOT)}")
    reset_output()
    shutil.copytree(DOCS, OUTPUT)
    shutil.copytree(STATIC_EXTRAS, OUTPUT, dirs_exist_ok=True)
    make_domain_neutral()
    metadata = write_release_metadata()
    write_manifest(metadata)
    write_archive()
    print(
        json.dumps(
            {
                "ok": True,
                "mode": metadata["deployment_mode"],
                "version": metadata["version"],
                "folder": str(OUTPUT),
                "archive": str(ARCHIVE),
                "archive_bytes": ARCHIVE.stat().st_size,
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
