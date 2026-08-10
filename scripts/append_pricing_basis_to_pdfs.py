#!/usr/bin/env python3
"""Append a current pricing-basis notice to public PDFs that contain money figures.

Source proposal PDFs retain their original scenarios. This script does not rewrite
scientific or historical content; it appends an explicit current-price notice and,
where an obsolete Care Mix formula is detected, places a supersession banner on
the affected page. The operation is idempotent.
"""
from __future__ import annotations

from pathlib import Path
import re

import fitz  # PyMuPDF

ROOT = Path(__file__).resolve().parents[1]
DOWNLOADS = ROOT / "docs" / "downloads"
FONT = next(
    path
    for path in (
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
    )
    if Path(path).exists()
)
BOLD = next(
    path
    for path in (
        "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf",
    )
    if Path(path).exists()
)

MARKER = "PRICING BASIS UPDATE 2026-08-10"
ACTIVE_PRICING_NAMES = {
    "GABA_Feed_Business_Model_Speech_Deck_v1.pdf",
    "셀핀다_가바크루드_국내외시장_사업전략기획서_v1.pdf",
}
MONEY_PATTERNS = [
    re.compile(r"\d[\d,]*(?:\.\d+)?\s*원"),
    re.compile(r"원/kg", re.I),
    re.compile(r"원/사료", re.I),
    re.compile(r"원가|가격|단가|ROI"),
]
STALE_PATTERNS = [
    re.compile(r"0\.5\s*kg\s*[×xX*]\s*7,?000\s*원"),
    re.compile(r"가바케어믹스[^\n]{0,120}5,?000\s*원/kg"),
    re.compile(r"가바크루드\s*50%[^\n]{0,100}5,?000\s*원/kg"),
    re.compile(r"4,681\.8\s*원/kg"),
]


def all_text(doc: fitz.Document) -> str:
    return "\n".join(page.get_text("text") for page in doc)


def has_money(text: str) -> bool:
    return any(pattern.search(text) for pattern in MONEY_PATTERNS)


def stale_pages(doc: fitz.Document) -> list[int]:
    pages: list[int] = []
    for number, page in enumerate(doc):
        text = page.get_text("text")
        if any(pattern.search(text) for pattern in STALE_PATTERNS):
            pages.append(number)
    return pages


def add_supersession_banner(page: fitz.Page) -> None:
    width = page.rect.width
    height = max(34, page.rect.height * 0.055)
    rect = fitz.Rect(0, 0, width, height)
    page.draw_rect(rect, color=(0.66, 0.18, 0.15), fill=(0.66, 0.18, 0.15), overlay=True)
    page.insert_font(fontname="NGB", fontfile=BOLD)
    page.insert_textbox(
        fitz.Rect(18, 7, width - 18, height - 4),
        "가격 산식 정정 · 이 페이지의 기존 Care Mix 원가 산식은 폐기되었습니다. 최신 기준은 문서 마지막의 Pricing Basis Update를 적용합니다.",
        fontname="NGB",
        fontsize=max(7.5, min(11, width / 95)),
        color=(1, 1, 1),
        align=fitz.TEXT_ALIGN_CENTER,
        overlay=True,
    )


def add_pricing_page(doc: fitz.Document, source_name: str, historical: bool) -> None:
    if len(doc):
        rect = doc[0].rect
    else:
        rect = fitz.Rect(0, 0, 842, 595)
    page = doc.new_page(width=rect.width, height=rect.height)
    page.insert_font(fontname="NG", fontfile=FONT)
    page.insert_font(fontname="NGB", fontfile=BOLD)

    w, h = rect.width, rect.height
    margin = max(30, w * 0.065)
    green = (0.043, 0.424, 0.31)
    dark = (0.09, 0.22, 0.17)
    gray = (0.35, 0.43, 0.39)
    mint = (0.92, 0.97, 0.94)

    page.draw_rect(rect, fill=(0.98, 0.99, 0.985), color=(0.98, 0.99, 0.985))
    page.insert_textbox(
        fitz.Rect(margin, margin * 0.65, w - margin, margin * 1.35),
        MARKER,
        fontname="NGB",
        fontsize=max(10, min(16, w / 58)),
        color=green,
    )
    page.insert_textbox(
        fitz.Rect(margin, margin * 1.45, w - margin, h * 0.28),
        "가바케어믹스 가격 산술 기준 정정",
        fontname="NGB",
        fontsize=max(22, min(38, w / 24)),
        color=dark,
    )
    subtitle = (
        "본 문서에 포함된 과거 예시가격·ROI 가정은 당시 시나리오이며 현재 공급 견적이 아닙니다."
        if historical
        else "현재 공개 기준가를 사용해 Care Mix 원료 투입 이론값을 다시 계산했습니다."
    )
    page.insert_textbox(
        fitz.Rect(margin, h * 0.255, w - margin, h * 0.36),
        subtitle,
        fontname="NG",
        fontsize=max(9, min(15, w / 62)),
        color=gray,
    )

    cards_y = h * 0.38
    cards_h = h * 0.25
    gap = w * 0.018
    card_w = (w - 2 * margin - 2 * gap) / 3
    cards = [
        ("가바크루드 공개 기준가", "18,000원/kg", "사용자 확정 공개 기준\nVAT·운송·거래조건 별도"),
        ("미네랄매트릭스", "3,000원/kg", "현재 산술용 잠정값\n실제 구매견적으로 갱신"),
        ("Care Mix 원료비", "10,500원/kg", "0.5kg×18,000 + 0.5kg×3,000\n사료 1톤당 1kg 적용 시 10,500원"),
    ]
    for index, (label, value, note) in enumerate(cards):
        x0 = margin + index * (card_w + gap)
        box = fitz.Rect(x0, cards_y, x0 + card_w, cards_y + cards_h)
        page.draw_rect(box, fill=mint, color=(0.78, 0.88, 0.82), width=1)
        page.insert_textbox(fitz.Rect(x0 + 12, cards_y + 12, x0 + card_w - 12, cards_y + 42), label, fontname="NGB", fontsize=max(8, min(12, w / 76)), color=green)
        page.insert_textbox(fitz.Rect(x0 + 12, cards_y + 45, x0 + card_w - 12, cards_y + 86), value, fontname="NGB", fontsize=max(17, min(26, w / 32)), color=dark)
        page.insert_textbox(fitz.Rect(x0 + 12, cards_y + 93, x0 + card_w - 12, cards_y + cards_h - 12), note, fontname="NG", fontsize=max(7.2, min(11, w / 88)), color=gray)

    note_y = cards_y + cards_h + h * 0.055
    page.insert_textbox(
        fitz.Rect(margin, note_y, w - margin, h - margin * 1.15),
        "중요: 10,500원/kg은 원료 2종만 반영한 이론 원료비이며 가바케어믹스 판매가격이 아닙니다. 최종 매출원가·공급단가는 혼합·제조·검사·포장·수율손실·물류·거래조건을 반영한 유효 견적서로 확정합니다.\n\n문서: " + source_name + "  ·  기준일: 2026-08-10  ·  문의: feed@cellpinda.com",
        fontname="NG",
        fontsize=max(8, min(12, w / 74)),
        color=dark,
        lineheight=1.45,
    )


def process(path: Path) -> str:
    if path.name == "GABA_Caremix_Specification_v1.pdf":
        return "generated-authoritative"
    doc = fitz.open(path)
    text = all_text(doc)
    if MARKER in text:
        doc.close()
        return "already-updated"

    stale = stale_pages(doc)
    should_append = path.name in ACTIVE_PRICING_NAMES or bool(stale) or has_money(text)
    if not should_append:
        doc.close()
        return "no-price-content"

    for page_no in stale:
        add_supersession_banner(doc[page_no])
    add_pricing_page(doc, path.name, historical=path.name not in ACTIVE_PRICING_NAMES)

    temp = path.with_suffix(".pricing.tmp.pdf")
    doc.save(temp, garbage=4, deflate=True, clean=True)
    doc.close()
    temp.replace(path)
    return f"updated:addendum;stale_pages={','.join(str(n + 1) for n in stale) or 'none'}"


def main() -> int:
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    results: dict[str, str] = {}
    for path in sorted(DOWNLOADS.glob("*.pdf")):
        results[path.name] = process(path)
    for name, status in results.items():
        print(f"{name}: {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
