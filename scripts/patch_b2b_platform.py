#!/usr/bin/env python3
"""Install B2B operating assets and harden inquiry/source-monitor routes."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "docs" / "index.html"
INQUIRY_UI = ROOT / "docs" / "assets" / "inquiry-form.js"
SOURCE_CONFIG = ROOT / "config" / "intelligence_sources_v2.json"
COLLECTOR = ROOT / "scripts" / "auto_intelligence_v2.py"
WORKER = ROOT / "scripts" / "build_site_worker.mjs"
DEPLOY = ROOT / ".github" / "workflows" / "deploy-public-index-v2.yml"

STYLE_TAG = '<link rel="stylesheet" href="assets/b2b-operations.css" data-b2b-operations="v1">'
SCRIPT_TAG = '<script src="assets/b2b-operations.js" defer data-b2b-operations="v1"></script>'


def replace_once(text: str, old: str, new: str, label: str) -> tuple[str, bool]:
    if new in text:
        return text, False
    if old not in text:
        raise RuntimeError(f"cannot locate patch target: {label}")
    return text.replace(old, new, 1), True


def patch_index(text: str) -> tuple[str, bool]:
    changed = False
    if STYLE_TAG not in text:
        anchor = '<link rel="stylesheet" href="assets/technical-documents.css" data-technical-documents="v1">'
        if anchor not in text:
            raise RuntimeError("technical-documents stylesheet reference not found")
        text = text.replace(anchor, anchor + "\n" + STYLE_TAG, 1)
        changed = True
    if SCRIPT_TAG not in text:
        anchor = '<script src="assets/technical-documents.js" defer data-technical-documents="v1"></script>'
        if anchor not in text:
            raise RuntimeError("technical-documents script reference not found")
        text = text.replace(anchor, anchor + SCRIPT_TAG, 1)
        changed = True
    return text, changed


def patch_inquiry_ui(text: str) -> tuple[str, bool]:
    changed = False
    replacements = [
        ("const RECIPIENT = 'dubaissday@cellpinda.com';", "const RECIPIENT = 'feed@cellpinda.com';", "legacy inquiry recipient"),
        ("const FORM_ENDPOINT = `https://formsubmit.co/${RECIPIENT}`;", "const FORM_ENDPOINT = '#';", "legacy FormSubmit endpoint"),
    ]
    for old, new, label in replacements:
        if old in text:
            text = text.replace(old, new, 1)
            changed = True
        elif new not in text:
            raise RuntimeError(f"cannot locate patch target: {label}")
    if "formsubmit.co" in text.lower():
        raise RuntimeError("formsubmit.co remains in inquiry-form.js")
    return text, changed


def patch_source_config(payload: dict) -> tuple[dict, bool]:
    changed = False
    updates = {
        "us-fda-animal-food": {
            "url": "https://www.fda.gov/animal-food-feeds",
            "urls": ["https://www.fda.gov/animal-food-feeds"],
        },
        "au-apvma-animal-feed": {
            "url": "https://www.apvma.gov.au/registrations-and-permits/chemical-product-registration/animal-feed-products",
            "urls": [
                "https://www.apvma.gov.au/registrations-and-permits/chemical-product-registration/animal-feed-products",
                "https://www.apvma.gov.au/registrations-and-permits/chemical-product-registration/acceptable-nutritional-messages"
            ],
        },
        "oecd-fao-agricultural-outlook": {
            "url": "https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035_47874669-en/full-report.html",
            "urls": [
                "https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035_47874669-en/full-report.html",
                "https://www.oecd.org/en/publications/oecd-fao-agricultural-outlook-2026-2035_47874669-en/full-report/key-messages_600831c0.html"
            ],
        },
    }
    monitors = payload.get("official_monitors", [])
    for monitor in monitors:
        patch = updates.get(monitor.get("id"))
        if not patch:
            continue
        for key, value in patch.items():
            if key == "urls":
                current_urls = monitor.get(key) or []
                merged_urls = list(current_urls)
                merged_urls.extend(url for url in value if url not in merged_urls)
                if current_urls != merged_urls:
                    monitor[key] = merged_urls
                    changed = True
            elif monitor.get(key) != value:
                monitor[key] = value
                changed = True
    missing = set(updates) - {row.get("id") for row in monitors}
    if missing:
        raise RuntimeError("missing source monitors: " + ", ".join(sorted(missing)))
    return payload, changed


OLD_MONITOR_BLOCK = '''        try:
            digest = visible_text_digest(request_bytes(source["url"]), source.get("keywords", []))
            next_state, confirmed = advance_monitor_state(state.get(sid, {}), digest, int(source.get("confirmation_runs", 2)))
            next_state["url"] = source["url"]
            state[sid] = next_state
            if confirmed or (not old_state.get(sid) and source.get("publish_initial", False)):
                category = source.get("category", "policy")
                item = Item(
                    item_id=f"{category}-{stable_id(sid, digest)}", category=category, source_type="official_monitor",
                    title=f"{source['name']} 관련 페이지 변경 확인 필요", summary="공식 출처의 관련 페이지에서 두 차례 연속 동일한 변경이 감지되었습니다. 변경 내용은 원문과 시행일을 확인한 뒤 사업 자료에 반영해야 합니다.",
                    source_name=source["name"], source_url=source["url"], published_at=now_utc().date().isoformat(), detected_at=iso_now(),
                    species=source.get("species", "Multi-species"), evidence_grade="A", confidence="high", official_source=True,
                    tags=[category, "official source", "confirmed change"], metadata={"source_id": sid, "content_hash": digest, "confirmation_runs": source.get("confirmation_runs", 2)},
                )
                items.append(quality_gate(item, config))
        except Exception as exc:  # monitoring must not stop research collection
            failures.append({"source": sid, "error": str(exc)[:300]})'''

NEW_MONITOR_BLOCK = '''        urls = [url for url in (source.get("urls") or [source.get("url")]) if url]
        active_url = ""
        last_error: Exception | None = None
        try:
            raw: bytes | None = None
            for candidate_url in urls:
                try:
                    raw = request_bytes(candidate_url)
                    active_url = candidate_url
                    break
                except Exception as exc:
                    last_error = exc
            if raw is None:
                raise last_error or RuntimeError(f"no monitor URL configured for {sid}")

            digest = visible_text_digest(raw, source.get("keywords", []))
            next_state, confirmed = advance_monitor_state(state.get(sid, {}), digest, int(source.get("confirmation_runs", 2)))
            next_state["url"] = active_url
            next_state["fallback_count"] = max(0, urls.index(active_url)) if active_url in urls else 0
            state[sid] = next_state
            if confirmed or (not old_state.get(sid) and source.get("publish_initial", False)):
                category = source.get("category", "policy")
                item = Item(
                    item_id=f"{category}-{stable_id(sid, digest)}", category=category, source_type="official_monitor",
                    title=f"{source['name']} 관련 페이지 변경 확인 필요", summary="공식 출처의 관련 페이지에서 두 차례 연속 동일한 변경이 감지되었습니다. 변경 내용은 원문과 시행일을 확인한 뒤 사업 자료에 반영해야 합니다.",
                    source_name=source["name"], source_url=active_url, published_at=now_utc().date().isoformat(), detected_at=iso_now(),
                    species=source.get("species", "Multi-species"), evidence_grade="A", confidence="high", official_source=True,
                    tags=[category, "official source", "confirmed change"], metadata={"source_id": sid, "content_hash": digest, "confirmation_runs": source.get("confirmation_runs", 2), "fallback_count": next_state["fallback_count"]},
                )
                items.append(quality_gate(item, config))
        except Exception as exc:  # monitoring must not stop research collection
            failures.append({"source": sid, "error": str(exc)[:300], "attempted_urls": urls})'''


def patch_collector(text: str) -> tuple[str, bool]:
    if NEW_MONITOR_BLOCK in text:
        return text, False
    # The collector may already contain the fallback implementation with
    # harmless formatting/comment changes from a previous release. Treat that
    # shape as installed so the CI installer remains idempotent.
    if (
        'source.get("urls")' in text
        and "active_url = \"\"" in text
        and 'metadata={"source_id": sid' in text
        and '"attempted_urls": urls' in text
    ):
        return text, False
    if OLD_MONITOR_BLOCK not in text:
        raise RuntimeError("official monitor block not found")
    return text.replace(OLD_MONITOR_BLOCK, NEW_MONITOR_BLOCK, 1), True


def patch_worker(text: str) -> tuple[str, bool]:
    changed = False
    entries = [
        ('  ["/assets/technical-documents.js", "assets/technical-documents.js", "text/javascript; charset=utf-8"],',
         '  ["/assets/technical-documents.js", "assets/technical-documents.js", "text/javascript; charset=utf-8"],\n  ["/assets/b2b-operations.css", "assets/b2b-operations.css", "text/css; charset=utf-8"],\n  ["/assets/b2b-operations.js", "assets/b2b-operations.js", "text/javascript; charset=utf-8"],'),
        ('  ["/data/technical_documents.json", "data/technical_documents.json", "application/json; charset=utf-8"],',
         '  ["/data/technical_documents.json", "data/technical_documents.json", "application/json; charset=utf-8"],\n  ["/data/b2b_operations.json", "data/b2b_operations.json", "application/json; charset=utf-8"],\n  ["/data/platform_health.json", "data/platform_health.json", "application/json; charset=utf-8"],'),
    ]
    for old, new in entries:
        if new in text:
            continue
        if old not in text:
            raise RuntimeError("worker insertion point not found")
        text = text.replace(old, new, 1)
        changed = True
    return text, changed


def patch_deploy(text: str) -> tuple[str, bool]:
    changed = False
    insertions = [
        ("          test -f docs/assets/technical-documents.js", "          test -f docs/assets/technical-documents.js\n          test -f docs/assets/b2b-operations.css\n          test -f docs/assets/b2b-operations.js"),
        ("          test -f docs/data/technical_documents.json", "          test -f docs/data/technical_documents.json\n          test -f docs/data/b2b_operations.json\n          test -f docs/data/platform_health.json"),
        ("          grep -q 'assets/technical-documents.js' docs/index.html", "          grep -q 'assets/technical-documents.js' docs/index.html\n          grep -q 'assets/b2b-operations.js' docs/index.html"),
        ("          node --check docs/assets/technical-documents.js", "          node --check docs/assets/technical-documents.js\n          node --check docs/assets/b2b-operations.js\n          python scripts/check_b2b_platform.py"),
        ('              Path("docs/data/technical_documents.json"),', '              Path("docs/data/technical_documents.json"),\n              Path("docs/data/b2b_operations.json"),\n              Path("docs/data/platform_health.json"),'),
    ]
    for old, new in insertions:
        if new in text:
            continue
        if old not in text:
            raise RuntimeError(f"deploy insertion point not found: {old}")
        text = text.replace(old, new, 1)
        changed = True
    return text, changed


def apply(check_only: bool = False) -> dict[str, bool]:
    results: dict[str, bool] = {}

    text = INDEX.read_text(encoding="utf-8")
    patched, changed = patch_index(text)
    results["index"] = changed
    if changed and not check_only:
        INDEX.write_text(patched, encoding="utf-8")

    text = INQUIRY_UI.read_text(encoding="utf-8")
    patched, changed = patch_inquiry_ui(text)
    results["inquiry"] = changed
    if changed and not check_only:
        INQUIRY_UI.write_text(patched, encoding="utf-8")

    payload = json.loads(SOURCE_CONFIG.read_text(encoding="utf-8"))
    payload, changed = patch_source_config(payload)
    results["source_config"] = changed
    if changed and not check_only:
        SOURCE_CONFIG.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    text = COLLECTOR.read_text(encoding="utf-8")
    patched, changed = patch_collector(text)
    results["collector"] = changed
    if changed and not check_only:
        COLLECTOR.write_text(patched, encoding="utf-8")

    text = WORKER.read_text(encoding="utf-8")
    patched, changed = patch_worker(text)
    results["worker"] = changed
    if changed and not check_only:
        WORKER.write_text(patched, encoding="utf-8")

    text = DEPLOY.read_text(encoding="utf-8")
    patched, changed = patch_deploy(text)
    results["deploy"] = changed
    if changed and not check_only:
        DEPLOY.write_text(patched, encoding="utf-8")

    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    results = apply(check_only=args.check)
    if args.check and any(results.values()):
        raise SystemExit("B2B platform patch is not fully installed: " + json.dumps(results, ensure_ascii=False))
    print(json.dumps(results, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
