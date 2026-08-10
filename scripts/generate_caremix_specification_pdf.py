from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "caremix_pricing_v1.json"
OUT = ROOT / "docs" / "downloads" / "GABA_Caremix_Specification_v1.pdf"

FONT_CANDIDATES = [
    ("/usr/share/fonts/truetype/nanum/NanumGothic.ttf", "/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf"),
    ("/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf", "/usr/share/fonts/truetype/nanum/NanumBarunGothicBold.ttf"),
]
FONT, FONT_B = next((a, b) for a, b in FONT_CANDIDATES if Path(a).exists() and Path(b).exists())
pdfmetrics.registerFont(TTFont("NanumGothic", FONT))
pdfmetrics.registerFont(TTFont("NanumGothic-Bold", FONT_B))

PAGE_W, PAGE_H = A4
GREEN = colors.HexColor("#0B6C4F")
DARK = colors.HexColor("#17382C")
MINT = colors.HexColor("#EAF5EF")
LIGHT = colors.HexColor("#F6F9F7")
BLUE = colors.HexColor("#155D91")
GOLD = colors.HexColor("#B1842F")
RED = colors.HexColor("#A84640")
GRAY = colors.HexColor("#66766E")
LINE = colors.HexColor("#D9E6DF")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="KTitle", fontName="NanumGothic-Bold", fontSize=27, leading=34, textColor=DARK, spaceAfter=8))
styles.add(ParagraphStyle(name="KSub", fontName="NanumGothic", fontSize=11.5, leading=18, textColor=GRAY, spaceAfter=8))
styles.add(ParagraphStyle(name="KHead", fontName="NanumGothic-Bold", fontSize=18, leading=24, textColor=DARK, spaceBefore=2, spaceAfter=10))
styles.add(ParagraphStyle(name="KHead2", fontName="NanumGothic-Bold", fontSize=12, leading=17, textColor=DARK, spaceBefore=4, spaceAfter=5))
styles.add(ParagraphStyle(name="KBody", fontName="NanumGothic", fontSize=9.3, leading=15, textColor=colors.HexColor("#344A40")))
styles.add(ParagraphStyle(name="KSmall", fontName="NanumGothic", fontSize=7.7, leading=12, textColor=GRAY))
styles.add(ParagraphStyle(name="KWhite", fontName="NanumGothic-Bold", fontSize=11, leading=15, textColor=colors.white))
styles.add(ParagraphStyle(name="KCardBig", fontName="NanumGothic-Bold", fontSize=20, leading=25, textColor=DARK))
styles.add(ParagraphStyle(name="KCardLabel", fontName="NanumGothic-Bold", fontSize=8.3, leading=11, textColor=GREEN))


def P(text: str, style: str = "KBody") -> Paragraph:
    return Paragraph(text, styles[style])


def header_footer(canvas, doc) -> None:
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(18 * mm, 14 * mm, PAGE_W - 18 * mm, 14 * mm)
    canvas.setFont("NanumGothic", 7)
    canvas.setFillColor(GRAY)
    canvas.drawString(18 * mm, 9.5 * mm, "CELLPINDA GABA CARE MIX · Pricing basis v1.2 · 2026-08-10")
    canvas.drawRightString(PAGE_W - 18 * mm, 9.5 * mm, str(doc.page))
    canvas.restoreState()


def section_title(no: str, title: str, subtitle: str | None = None) -> list:
    parts = [
        Table(
            [[P(no, "KWhite"), P(title, "KHead")]],
            colWidths=[18 * mm, 150 * mm],
            style=TableStyle(
                [
                    ("BACKGROUND", (0, 0), (0, 0), GREEN),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("BOX", (0, 0), (-1, -1), 0, colors.transparent),
                    ("LEFTPADDING", (0, 0), (0, 0), 6),
                    ("RIGHTPADDING", (0, 0), (0, 0), 6),
                    ("TOPPADDING", (0, 0), (0, 0), 6),
                    ("BOTTOMPADDING", (0, 0), (0, 0), 6),
                    ("LEFTPADDING", (1, 0), (1, 0), 9),
                ]
            ),
        )
    ]
    if subtitle:
        parts += [P(subtitle, "KSub"), Spacer(1, 2 * mm)]
    return parts


def callout(title: str, body: str, bg=MINT, color=GREEN) -> Table:
    return Table(
        [[P(title, "KHead2"), P(body, "KBody")]],
        colWidths=[42 * mm, 126 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), bg),
                ("BOX", (0, 0), (-1, -1), 0.7, color),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 9),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
            ]
        ),
    )


def card(label: str, value: str, body: str, accent=GREEN) -> Table:
    return Table(
        [[P(label, "KCardLabel")], [P(value, "KCardBig")], [P(body, "KSmall")]],
        colWidths=[39 * mm],
        style=TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.white),
                ("BOX", (0, 0), (-1, -1), 0.8, LINE),
                ("LINEABOVE", (0, 0), (0, 0), 3, accent),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        ),
    )


def data_table(data: list[list], widths: list, header: bool = True, font_size: float = 8.3) -> Table:
    style = [
        ("FONTNAME", (0, 0), (-1, -1), "NanumGothic"),
        ("FONTSIZE", (0, 0), (-1, -1), font_size),
        ("LEADING", (0, 0), (-1, -1), 12),
        ("TEXTCOLOR", (0, 0), (-1, -1), DARK),
        ("GRID", (0, 0), (-1, -1), 0.5, LINE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]
    if header:
        style += [
            ("BACKGROUND", (0, 0), (-1, 0), DARK),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "NanumGothic-Bold"),
        ]
        for row in range(1, len(data)):
            if row % 2 == 0:
                style.append(("BACKGROUND", (0, row), (-1, row), LIGHT))
    return Table(data, colWidths=widths, repeatRows=1 if header else 0, style=TableStyle(style))


def build_pdf() -> None:
    cfg = json.loads(CONFIG.read_text(encoding="utf-8"))
    crude_price = int(cfg["gaba_crude"]["public_supply_price_krw_per_kg"])
    mineral_price = int(cfg["mineral_matrix"]["price_krw_per_kg"])
    caremix_cost = int(cfg["care_mix"]["calculated_raw_material_cost_krw_per_kg"])

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=17 * mm,
        bottomMargin=18 * mm,
        title="GABA Care Mix 기술·사업 사양서 v1.2",
        author="Cellpinda Life Science Lab",
    )
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header_footer)])
    story: list = []

    story += [
        P("PRODUCT SPECIFICATION · PRICING BASIS v1.2", "KCardLabel"),
        Spacer(1, 3 * mm),
        P("GABA Care Mix<br/>가바케어믹스 기술·사업 사양서", "KTitle"),
        P("가바크루드 GABA 20% 기준품과 미네랄매트릭스를 50:50으로 배합하여, 사료 1톤당 1kg 투입 시 명목 GABA 100mg/kg을 공급하는 제품 설계안입니다.", "KSub"),
        Spacer(1, 5 * mm),
        Table(
            [[
                card("GABA CRUDE", f"{crude_price:,}원/kg", "셀핀다 공개 공급 기준가<br/>VAT·운송 등 별도", GREEN),
                card("MINERAL MATRIX", f"{mineral_price:,}원/kg", "사용자 확정 공개 기준<br/>VAT·운송 등 별도", BLUE),
                card("CARE MIX 원료비", f"{caremix_cost:,}원/kg", "50:50 혼합 원료 2종만 반영<br/>제조·검사·포장 등 제외", GOLD),
                card("사료 1톤당", f"{caremix_cost:,}원", "Care Mix 1kg 투입 기준<br/>최종 공급가와 구분", RED),
            ]],
            colWidths=[42 * mm] * 4,
            style=TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2)]),
        ),
        Spacer(1, 6 * mm),
        callout("핵심 산식", f"<b>0.5kg × {crude_price:,}원 + 0.5kg × {mineral_price:,}원 = {caremix_cost:,}원/kg</b><br/>기존 공개 산식은 가바크루드 기준가가 일치하지 않아 폐기합니다.", colors.HexColor("#FFF4E5"), GOLD),
        Spacer(1, 5 * mm),
        callout("가격 구분", f"<b>{caremix_cost:,}원/kg은 원료 투입 이론값이며 판매가격이 아닙니다.</b><br/>최종 공급단가는 혼합·제조·검사·포장·수율손실·물류·판매조건을 반영한 유효 견적서로 확정합니다."),
        Spacer(1, 7 * mm),
        data_table(
            [
                [P("구분", "KWhite"), P("적용 기준", "KWhite"), P("상태", "KWhite")],
                [P("가바크루드 기준가"), P(f"{crude_price:,}원/kg"), P("사용자 확정 공개 기준")],
                [P("미네랄매트릭스"), P(f"{mineral_price:,}원/kg"), P("사용자 확정 공개 기준")],
                [P("Care Mix 배합"), P("가바크루드 50% + 미네랄매트릭스 50%"), P("제품 설계안")],
                [P("Care Mix 원료비"), P(f"{caremix_cost:,}원/kg · 사료 1톤당 {caremix_cost:,}원"), P("원료 2종 이론값")],
                [P("Care Mix 공급가"), P("별도 견적"), P("미확정")],
            ],
            [45 * mm, 78 * mm, 45 * mm],
        ),
        PageBreak(),
    ]

    story += section_title("01", "제품 설계와 산술 기준", "GABA 함량과 배합량은 질량수지로 계산하고, 가격은 공개 공급 기준가와 최종 매출원가를 구분합니다.")
    story += [
        P("1. GABA 질량수지", "KHead2"),
        data_table(
            [
                [P("계산 단계", "KWhite"), P("산식", "KWhite"), P("결과", "KWhite")],
                [P("목표 GABA"), P("사료 1,000kg × 100mg/kg"), P("GABA 100g")],
                [P("가바크루드 필요량"), P("GABA 100g ÷ 20%"), P("가바크루드 500g")],
                [P("Care Mix 배합"), P("가바크루드 500g + 미네랄매트릭스 500g"), P("Care Mix 1kg")],
                [P("Care Mix GABA 함량"), P("GABA 100g ÷ Care Mix 1kg"), P("GABA 10%")],
                [P("최종 투입"), P("Care Mix 1kg / 사료 1톤"), P("명목 GABA 100mg/kg")],
            ],
            [44 * mm, 78 * mm, 46 * mm],
        ),
        Spacer(1, 5 * mm),
        P("2. 원료 투입원가", "KHead2"),
        data_table(
            [
                [P("원료", "KWhite"), P("배합량", "KWhite"), P("기준단가", "KWhite"), P("금액", "KWhite"), P("근거상태", "KWhite")],
                [P("가바크루드 20"), P("0.500kg"), P(f"{crude_price:,}원/kg"), P(f"{crude_price * 0.5:,.0f}원"), P("사용자 확정 공개 기준")],
                [P("미네랄매트릭스"), P("0.500kg"), P(f"{mineral_price:,}원/kg"), P(f"{mineral_price * 0.5:,.0f}원"), P("사용자 확정 공개 기준")],
                [P("합계"), P("1.000kg"), P("-"), P(f"<b>{caremix_cost:,}원</b>"), P("원료 2종만 반영")],
            ],
            [38 * mm, 27 * mm, 35 * mm, 30 * mm, 38 * mm],
        ),
        Spacer(1, 5 * mm),
        callout("산술 검증", f"0.5 × {crude_price:,} = {crude_price * 0.5:,.0f}원<br/>0.5 × {mineral_price:,} = {mineral_price * 0.5:,.0f}원<br/><b>{crude_price * 0.5:,.0f} + {mineral_price * 0.5:,.0f} = {caremix_cost:,}원/kg</b>", LIGHT, GREEN),
        Spacer(1, 5 * mm),
        data_table(
            [
                [P("가격 용어", "KWhite"), P("정의", "KWhite"), P("현재 상태", "KWhite")],
                [P("원료 투입원가"), P("가바크루드와 미네랄매트릭스 자체 금액"), P(f"{caremix_cost:,}원/kg")],
                [P("매출원가"), P("원료비 + 제조·혼합·검사·포장·수율손실 등"), P("견적·시험생산 후 확정")],
                [P("공급단가"), P("매출원가 + 물류·거래조건·마진 등"), P("유효 견적서로 확정")],
            ],
            [38 * mm, 89 * mm, 41 * mm],
        ),
        PageBreak(),
    ]

    story += section_title("02", "가바케어믹스 단가 민감도", "미네랄매트릭스 기준가 또는 배합비가 변경되면 Care Mix 원료비를 같은 버전으로 재산정합니다.")
    scenarios = []
    for mineral in [3000, 4000, 5000, 6000, 7000]:
        mineral_component = 0.5 * mineral
        total = 0.5 * crude_price + mineral_component
        scenarios.append([P(f"{mineral:,.0f}원/kg"), P(f"{crude_price * 0.5:,.0f}원"), P(f"{mineral_component:,.0f}원"), P(f"<b>{total:,.0f}원/kg</b>"), P(f"{total:,.0f}원/사료톤")])
    story += [
        data_table([[P("미네랄 기준가", "KWhite"), P("가바크루드 50%", "KWhite"), P("미네랄 50%", "KWhite"), P("Care Mix 원료비", "KWhite"), P("1kg/t 적용비", "KWhite")]] + scenarios, [34 * mm, 34 * mm, 31 * mm, 38 * mm, 38 * mm]),
        Spacer(1, 6 * mm),
        callout("현재 공개 기준", f"<b>미네랄매트릭스 {mineral_price:,}원/kg 기준 → Care Mix 원료비 {caremix_cost:,}원/kg</b><br/>기준가 또는 배합비가 변경되면 본 표와 웹·PDF·견적 템플릿을 같은 버전으로 갱신합니다."),
        Spacer(1, 6 * mm),
        P("최종 공급단가 구성", "KHead2"),
        data_table(
            [[P("단계", "KWhite"), P("구성항목", "KWhite"), P("금액", "KWhite"), P("확정방법", "KWhite")]]
            + [[P(a), P(b), P(c), P(d)] for a, b, c, d in [
                ("A", "원료 투입원가", f"{caremix_cost:,}원/kg", "현재 계산 가능"),
                ("B", "혼합·제조비", "견적 필요", "OEM·공정조건"),
                ("C", "검사·CoA", "견적 필요", "시험항목·빈도"),
                ("D", "포장·라벨", "견적 필요", "포장단위·재질"),
                ("E", "수율손실·폐기", "시험생산 필요", "실제 회수율"),
                ("F", "물류·거래조건·마진", "계약 필요", "수량·Incoterm"),
            ]],
            [20 * mm, 58 * mm, 42 * mm, 48 * mm],
        ),
        Spacer(1, 6 * mm),
        callout("공개 원칙", f"원료 투입원가 {caremix_cost:,}원/kg을 가바케어믹스 판매가격으로 표시하지 않습니다. 최종 공급단가는 위 A~F를 모두 반영한 견적서로만 확정합니다.", colors.HexColor("#FFF2F1"), RED),
        PageBreak(),
    ]

    story += section_title("03", "적용·혼합·파일럿 가이드", "Care Mix는 저투입량 제품이므로 균일 혼합과 완제품 함량 확인이 필수입니다.")
    story += [
        data_table(
            [
                [P("항목", "KWhite"), P("검토 기준", "KWhite"), P("확인자료", "KWhite")],
                [P("투입량"), P("Care Mix 1kg/사료 1톤"), P("배치기록·계량기록")],
                [P("혼합"), P("단계희석 또는 프리믹스 공정으로 균일도 확보"), P("혼합시간·CV·3지점 시료")],
                [P("GABA 함량"), P("Care Mix GABA 10%, 최종 사료 명목 100mg/kg"), P("원료·완제품 HPLC")],
                [P("공정안정성"), P("펠릿·열·수분 조건에 따른 함량 유지 확인"), P("공정 전후 비교시험")],
                [P("보관"), P("고온·습기·직사광선 회피, 밀봉"), P("안정성·보존시험")],
            ],
            [34 * mm, 86 * mm, 48 * mm],
        ),
        Spacer(1, 6 * mm),
        P("축종별 파일럿 KPI", "KHead2"),
        data_table(
            [
                [P("대상", "KWhite"), P("시험방향", "KWhite"), P("우선 KPI", "KWhite")],
                [P("씨돼지"), P("고온기 4~8주 대조시험"), P("섭취량·체중·cortisol·정액량·운동성·이상정자율")],
                [P("비육돈"), P("생산주기·기초성적 반영"), P("ADG·ADFI·FCR·건물소화율·행동")],
                [P("한우·육우·와규"), P("일부 군부터 단계 적용"), P("DMI·ADG·FCR·체온·육색·TBARS·등급·ROI")],
                [P("젖소"), P("열 스트레스 구간 포함"), P("DMI·유량·유성분·체온·스트레스·경제성")],
                [P("가금"), P("육계·산란계 생산주기 반영"), P("BWG·FCR·폐사·H/L ratio·산란·TBARS")],
            ],
            [34 * mm, 57 * mm, 77 * mm],
        ),
        Spacer(1, 6 * mm),
        callout("효능 표현", "성장·FCR·장 건강·육질·번식지표는 연구결과 또는 파일럿 가설로 표시합니다. 메탄저감·탄소배출권은 완제품 직접시험과 제3자 검증 전까지 별도 연구프로젝트입니다.", colors.HexColor("#FFF8E8"), GOLD),
        PageBreak(),
    ]

    story += section_title("04", "상업 전환 체크리스트", "제품 규격과 가격은 같은 버전으로 승인하고, 로트별 품질자료와 실제 견적을 연결합니다.")
    story += [
        data_table(
            [
                [P("게이트", "KWhite"), P("필수자료", "KWhite"), P("완료기준", "KWhite")],
                [P("제품규격"), P("GABA 함량·성상·수분·미생물·중금속·입도"), P("승인 규격서와 분석법")],
                [P("원료가격"), P("가바크루드 기준가·미네랄 구매견적"), P("유효기간이 있는 견적서")],
                [P("제조원가"), P("혼합·제조·검사·포장·수율·폐기"), P("시험생산 실적과 매출원가표")],
                [P("공급단가"), P("MOQ·포장·납기·물류·결제조건·마진"), P("고객별 최종 견적")],
                [P("품질"), P("로트 CoA·추적·변경·일탈·회수 절차"), P("QA Agreement")],
                [P("현장검증"), P("대조군·KPI·시험기간·중단기준"), P("승인된 파일럿 프로토콜")],
                [P("규제"), P("국가별 사료분류·표시·효능문구"), P("서면 검토 완료")],
            ],
            [33 * mm, 78 * mm, 57 * mm],
        ),
        Spacer(1, 7 * mm),
        P("가격 승인 블록", "KHead2"),
        data_table(
            [
                [P("항목", "KWhite"), P("현재 값", "KWhite"), P("승인 상태", "KWhite")],
                [P("가바크루드 공개 기준가"), P(f"{crude_price:,}원/kg"), P("적용")],
                [P("미네랄매트릭스 기준가"), P(f"{mineral_price:,}원/kg"), P("잠정 - 견적 필요")],
                [P("Care Mix 원료 투입원가"), P(f"{caremix_cost:,}원/kg"), P("이론 산술 적용")],
                [P("Care Mix 최종 매출원가"), P("미확정"), P("시험생산·견적 후 승인")],
                [P("Care Mix 최종 공급단가"), P("미확정"), P("고객 견적서로 승인")],
            ],
            [59 * mm, 55 * mm, 54 * mm],
        ),
        Spacer(1, 7 * mm),
        callout("버전관리", "본 문서는 2026-08-10 기준 가격 산술 정정본 v1.2입니다. 가바크루드 기준가, 미네랄매트릭스 견적 또는 배합비가 변경되면 문서·웹·계산기·견적 템플릿을 같은 버전으로 갱신합니다."),
        Spacer(1, 6 * mm),
        P("근거 및 범위", "KHead2"),
        P(f"가바크루드 {crude_price:,}원/kg은 사용자 확정 공개 기준입니다. 미네랄매트릭스 {mineral_price:,}원/kg도 사용자 확정 공개 기준이며, 제공 자료에는 최종 구매견적·혼합 제조비·검사비·포장비·실제 수율이 없습니다. 따라서 {caremix_cost:,}원/kg은 원료 2종의 이론 투입원가로만 사용합니다. 제품효능은 축종별 대조시험으로 확인합니다."),
        Spacer(1, 5 * mm),
        HRFlowable(width="100%", thickness=0.6, color=LINE),
        Spacer(1, 3 * mm),
        P("Business inquiry · feed@cellpinda.com", "KSmall"),
    ]

    doc.build(story)


if __name__ == "__main__":
    build_pdf()
    print(OUT)
