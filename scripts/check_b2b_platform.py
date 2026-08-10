#!/usr/bin/env python3
"""Generate a public, non-secret health snapshot for the B2B operating platform."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "data" / "platform_health.json"


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


def parse_datetime(value: str) -> datetime | None:
    value = str(value or "").strip()
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc)
    except ValueError:
        return None


def main() -> int:
    now = datetime.now(timezone.utc)
    checks: list[dict[str, Any]] = []

    def add(check_id: str, label: str, ok: bool, severity: str, message: str) -> None:
        checks.append({
            "id": check_id,
            "label": label,
            "ok": bool(ok),
            "severity": severity,
            "message": message,
        })

    required_files = [
        DOCS / "index.html",
        DOCS / "assets" / "b2b-operations.css",
        DOCS / "assets" / "b2b-operations.js",
        DOCS / "assets" / "smart-consultation.css",
        DOCS / "assets" / "smart-consultation.js",
        DOCS / "assets" / "technical-documents.js",
        DOCS / "data" / "b2b_operations.json",
        DOCS / "data" / "technical_documents.json",
        DOCS / "data" / "update_status.json",
        DOCS / "assets" / "inquiry-form.js",
        DOCS / "assets" / "inquiry-apps-script.js",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_files if not path.exists()]
    add(
        "required_files",
        "필수 공개자산",
        not missing,
        "critical",
        "모든 필수자산 존재" if not missing else "누락: " + ", ".join(missing),
    )

    index = read_text(DOCS / "index.html")
    loader = read_text(DOCS / "assets" / "technical-documents.js")
    direct_refs = all(ref in index for ref in ("assets/b2b-operations.css", "assets/b2b-operations.js"))
    loader_refs = all(ref in loader for ref in ("assets/b2b-operations.css", "assets/b2b-operations.js"))
    assets_connected = direct_refs or loader_refs
    add(
        "asset_references",
        "B2B 운영모듈 연결",
        assets_connected,
        "critical",
        "직접 연결됨" if direct_refs else ("기술자료 로더를 통해 연결됨" if loader_refs else "B2B CSS·JavaScript 연결 누락"),
    )

    smart_js = read_text(DOCS / "assets" / "smart-consultation.js")
    smart_connected = (
        "assets/smart-consultation.js" in loader
        and "조건 검토 후 상담요청" in smart_js
        and "스마트상담_진입경로" in smart_js
        and "smartConditionalFields" in smart_js
    )
    add(
        "smart_consultation",
        "조건기반 스마트 상담",
        smart_connected,
        "critical",
        "도입진단·주문가이드·Buyer Pack 조건 자동반영" if smart_connected else "스마트 상담 로더·자동설정 필드 확인 필요",
    )

    inquiry_ui = read_text(DOCS / "assets" / "inquiry-form.js")
    inquiry_route = read_text(DOCS / "assets" / "inquiry-apps-script.js")
    inquiry_server = read_text(ROOT / "apps-script" / "Inquiry_v2.gs")
    legacy_formsubmit = "formsubmit.co" in inquiry_ui.lower()
    legacy_recipient = "dubaissday@cellpinda.com" in inquiry_ui.lower()
    runtime_route_ok = (
        "feed@cellpinda.com" in inquiry_route
        and "script.google.com/macros/s/" in inquiry_route
        and "feed@cellpinda.com" in inquiry_server
        and "doPost" in inquiry_server
    )
    add(
        "inquiry_runtime_route",
        "실제 문의 수신경로",
        runtime_route_ok,
        "critical",
        "Apps Script → feed@cellpinda.com" if runtime_route_ok else "Apps Script URL·수신주소·doPost 설정 확인 필요",
    )
    add(
        "legacy_inquiry_transport",
        "구형 문의전송 코드",
        not (legacy_formsubmit or legacy_recipient),
        "warning",
        "구형 전송경로 제거됨" if not (legacy_formsubmit or legacy_recipient) else "구형 FormSubmit 코드가 원본 UI에 남아 있으나 신규 Apps Script 라우터가 실행 시 덮어씀. 완전 제거 필요",
    )

    operations = load_json(DOCS / "data" / "b2b_operations.json", {})
    stage_count = len(operations.get("stages", [])) if isinstance(operations, dict) else 0
    pack_count = len(operations.get("buyer_packs", [])) if isinstance(operations, dict) else 0
    operations_ok = stage_count >= 6 and pack_count >= 4
    add(
        "operating_model",
        "바이어 운영모델",
        operations_ok,
        "critical",
        f"운영단계 {stage_count}개 · 바이어팩 {pack_count}개",
    )

    documents = load_json(DOCS / "data" / "technical_documents.json", {})
    document_count = len(documents.get("items", [])) if isinstance(documents, dict) else 0
    add(
        "documents",
        "기술·사업 자료",
        document_count >= 7,
        "warning",
        f"공개 자료 {document_count}건",
    )

    source_config = load_json(ROOT / "config" / "intelligence_sources_v2.json", {})
    monitors = source_config.get("official_monitors", []) if isinstance(source_config, dict) else []
    monitor_map = {row.get("id"): row for row in monitors if isinstance(row, dict)}
    fallback_ok = all(
        isinstance(monitor_map.get(source_id, {}).get("urls"), list)
        and monitor_map[source_id]["urls"]
        for source_id in (
            "us-fda-animal-food",
            "au-apvma-animal-feed",
            "oecd-fao-agricultural-outlook",
        )
    )
    add(
        "official_source_fallbacks",
        "공식출처 대체경로",
        fallback_ok,
        "warning",
        "FDA·APVMA·OECD 기본·대체 URL 구성" if fallback_ok else "핵심 공식출처의 대체 URL 보완 필요",
    )

    update_status = load_json(DOCS / "data" / "update_status.json", {})
    updated_at = parse_datetime(update_status.get("updated_at", "")) if isinstance(update_status, dict) else None
    age_hours = round((now - updated_at).total_seconds() / 3600, 1) if updated_at else None
    fresh = age_hours is not None and age_hours <= 72
    add(
        "data_freshness",
        "자동자료 최신성",
        fresh,
        "warning",
        f"마지막 갱신 {age_hours}시간 전" if age_hours is not None else "갱신시각 확인 불가",
    )

    intelligence_status = str(update_status.get("status", "unknown")) if isinstance(update_status, dict) else "unknown"
    failure_count = len(update_status.get("failures", [])) if isinstance(update_status, dict) else 0
    add(
        "intelligence_sources",
        "외부 인텔리전스 수집",
        intelligence_status == "healthy",
        "warning",
        f"상태 {intelligence_status} · 실패 소스 {failure_count}개",
    )

    add(
        "inquiry_e2e",
        "문의 종단간 운영시험",
        False,
        "warning",
        "통제된 테스트 문의로 페이지 문의번호·feed 메일·백업메일·Inquiries 행을 함께 확인해야 함",
    )

    critical_failed = sum(1 for check in checks if check["severity"] == "critical" and not check["ok"])
    warning_failed = sum(1 for check in checks if check["severity"] == "warning" and not check["ok"])
    overall = "degraded" if critical_failed else ("partial" if warning_failed else "healthy")

    payload = {
        "schema_version": "1.2.0",
        "generated_at": now.replace(microsecond=0).isoformat(),
        "status": overall,
        "summary": {
            "critical_failed": critical_failed,
            "warnings": warning_failed,
            "checks": len(checks),
            "documents": document_count,
            "operating_stages": stage_count,
            "buyer_packs": pack_count,
            "smart_consultation": smart_connected,
        },
        "checks": checks,
        "heartbeat": {
            key: update_status.get(key, "")
            for key in (
                "last_run_at", "last_success_at", "last_content_change_at",
                "workflow_run_id", "workflow_attempt", "trigger_type",
                "sources_total", "sources_success", "sources_failed",
                "items_collected_this_run", "items_published_current",
                "review_queue_current",
            )
        },
        "public_note": "본 상태는 공개자산·스마트 상담·데이터 최신성·문의 설정을 점검한 비민감 운영 스냅샷입니다. 실제 메일 수신과 응답시간은 통제된 운영시험으로 별도 확인합니다.",
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload["summary"], ensure_ascii=False))
    return 1 if critical_failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
