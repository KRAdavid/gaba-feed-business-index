#!/usr/bin/env python3
"""Audit user-facing Korean copy before the GABA index is published."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


ROOT = Path(__file__).resolve().parents[1]
TEXT_FILES = (
    ROOT / "docs" / "index.html",
    ROOT / "docs" / "404.html",
    ROOT / "docs" / "assets" / "app.js",
    ROOT / "docs" / "data" / "index.json",
    ROOT / "data" / "base_index.json",
    ROOT / "data" / "manual_signals.json",
    ROOT / "GABA_Index_운영가이드.md",
    ROOT / "README.md",
    ROOT / "GABA_Index_Artifact.json",
    ROOT / "GABA_Business_Model_Index.html",
    ROOT / "_work" / "deck" / "build_speech_deck.mjs",
    ROOT / "_work" / "model" / "build_gaba_index_workbook.mjs",
)
PRESENTATION = ROOT / "GABA_Feed_Business_Model_Speech_Deck_v1.pptx"

# These expressions made the earlier copy sound like translated software copy or
# an automatically generated slogan. The audit keeps them out of public outputs.
FORBIDDEN_EXPRESSIONS = (
    "잠금",
    "잠그",
    "잠길",
    "열린 게이트",
    "게이트가 열",
    "게이트가 닫",
    "열려 있",
    "닫혀야",
    "해제 근거",
    "다음 결정을 명확하게",
    "Evidence before scale",
    "원가 브리지",
    "제품특이",
    "반복 PO 트리거",
    "반복주문 트리거",
    "사료업계 비경험자",
    "90일 안에 잠글 것",
    "Source for ",
    "구장룡",
)


def read_presentation_text(path: Path) -> tuple[str, int, str]:
    if not path.exists():
        return "", 0, ""
    slide_rows: list[tuple[int, str]] = []
    with zipfile.ZipFile(path) as archive:
        names = [name for name in archive.namelist() if re.fullmatch(r"ppt/slides/slide\d+\.xml", name)]
        for name in names:
            number = int(re.search(r"slide(\d+)\.xml", name).group(1))
            root = ET.fromstring(archive.read(name))
            text = " ".join(node.text or "" for node in root.iter() if node.tag.endswith("}t"))
            slide_rows.append((number, text))
    slide_rows.sort()
    combined = "\n".join(text for _, text in slide_rows)
    final_text = slide_rows[-1][1] if slide_rows else ""
    return combined, len(slide_rows), final_text


def audit_copy() -> list[str]:
    errors: list[str] = []
    checked: list[tuple[str, str]] = []
    for path in TEXT_FILES:
        if not path.exists():
            errors.append(f"감리 대상 파일이 없습니다: {path.relative_to(ROOT)}")
            continue
        checked.append((str(path.relative_to(ROOT)), path.read_text(encoding="utf-8-sig")))

    deck_text, slide_count, final_slide = read_presentation_text(PRESENTATION)
    if not deck_text:
        errors.append(f"감리 대상 발표자료가 없습니다: {PRESENTATION.name}")
    else:
        checked.append((PRESENTATION.name, deck_text))
        if slide_count != 20:
            errors.append(f"발표자료 장수가 20장이 아닙니다: {slide_count}장")
        if "APPENDIX" not in final_slide.upper():
            errors.append("발표자료의 마지막 장이 APPENDIX가 아닙니다.")

    for name, text in checked:
        for expression in FORBIDDEN_EXPRESSIONS:
            if expression in text:
                errors.append(f"어색한 표현이 남아 있습니다: {name} → {expression}")
        if re.search(r"[가-힣][ ]{2,}[가-힣]", text):
            errors.append(f"한국어 문장에 불필요한 연속 공백이 있습니다: {name}")

    html = (ROOT / "docs" / "index.html").read_text(encoding="utf-8-sig")
    if "처음에는 네 가지 정보만 확인하세요." not in html:
        errors.append("첫 화면의 안내 문구가 네 개 요약 카드와 일치하지 않습니다.")
    if "APPENDIX · 부록" not in html:
        errors.append("공개 사이트의 마지막 섹션에 APPENDIX · 부록 표기가 없습니다.")
    return errors


def main() -> None:
    errors = audit_copy()
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print(
        json.dumps(
            {
                "ok": True,
                "audit": "korean-copy",
                "text_files": len(TEXT_FILES),
                "presentation": PRESENTATION.name,
                "slides": 20,
                "forbidden_expressions": len(FORBIDDEN_EXPRESSIONS),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
