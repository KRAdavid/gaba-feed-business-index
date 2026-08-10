from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "GABA_Feed_Business_Model_Speech_Deck_v1.pdf"
FONT = "NotoSansKR"
pdfmetrics.registerFont(TTFont(FONT, r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont(FONT + "-Bold", r"C:\Windows\Fonts\malgunbd.ttf"))

PAGE = landscape(A4)
styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Title"], fontName=FONT+"-Bold", fontSize=28, leading=36, textColor=colors.HexColor("#101828"), spaceAfter=12)
subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontName=FONT, fontSize=14, leading=22, textColor=colors.HexColor("#475467"))
head = ParagraphStyle("head", parent=styles["Heading2"], fontName=FONT+"-Bold", fontSize=21, leading=28, textColor=colors.HexColor("#101828"), spaceAfter=14)
body = ParagraphStyle("body", parent=styles["BodyText"], fontName=FONT, fontSize=13, leading=21, textColor=colors.HexColor("#344054"), spaceAfter=9)
small = ParagraphStyle("small", parent=body, fontSize=9, leading=14, textColor=colors.HexColor("#667085"))

def P(text, style=body):
    return Paragraph(text, style)

def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D0D5DD")); canvas.line(18*mm, 13*mm, 279*mm, 13*mm)
    canvas.setFont(FONT, 8); canvas.setFillColor(colors.HexColor("#667085"))
    canvas.drawString(18*mm, 8*mm, "GABA 사료 비즈니스 모델 | 공개 검토용 스피치덱")
    canvas.drawRightString(279*mm, 8*mm, f"{doc.page}")
    canvas.restoreState()

def page(title_text, kicker, paragraphs, table=None):
    story = [P(kicker.upper(), small), P(title_text, title)]
    story += [P(x) for x in paragraphs]
    if table:
        t = Table([[P(str(c), small) for c in row] for row in table], colWidths=[55*mm, 75*mm, 115*mm])
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.HexColor("#E8F5F0")), ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#D0D5DD")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("LEFTPADDING", (0,0), (-1,-1), 8), ("RIGHTPADDING", (0,0), (-1,-1), 8), ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
        story += [Spacer(1, 6*mm), t]
    return story

story = []
story += [Spacer(1, 28*mm), P("가바 사료 비즈니스 모델", title), P("가바크루드 원료와 가바케어믹스 배합사료를 이원화한 사업화 제안", subtitle), Spacer(1, 12*mm), P("사료업체·투자자 공개 검토용 | 2026년 8월", small), PageBreak()]
story += page("왜 지금 가바크루드에 집중해야 하는가", "01 · functional feed trend", ["기능성 사료의 구매 기준은 새로운 성분 자체보다 생산성, 규격의 재현성, 지속가능성 지표를 함께 설명할 수 있는가에 있습니다.", "OECD·FAO는 축산 생산성 향상, 사료 효율 개선, 사료 고도화를 주요 과제로 제시합니다. 가바크루드는 효능 주장보다 먼저 GABA 20% 표준품과 로트별 CoA를 제시해, 고객의 검증과 구매 판단을 돕는 원료로 포지셔닝합니다.", "출처: OECD-FAO Agricultural Outlook 2025-2034. 가바 관련 효능은 축종별 별도 시험으로 확인합니다."], [["기능성 사료 흐름", "생산성·검증·지속가능성", "효과 방향과 근거를 함께 확인하려는 구매 기준"], ["가바크루드 역할", "GABA 20% 표준품", "로트·CoA·OEM 농도·원가를 표준화해 고객 배합사료로 확장"], ["사업화 전환", "유료 시험 → 재주문", "원료 규격 → 시험성적 → 반복 주문으로 이어지는 단계적 확장"]])+[PageBreak()]
story += page("가바크루드 영업전략", "02 · go-to-market", ["국내는 사료회사 연구개발·구매팀과 축종 전문 배합사료 브랜드를 중심으로, 규격서와 샘플을 제시한 뒤 소규모 유료 시험으로 빠르게 진입합니다.", "해외는 기능성 원료 유통사와 현지 사료공장을 대상으로 국가별 품목·표시 요건을 먼저 확인하고, 현지 소규모 시험과 유통 파트너 검증 후 최소주문량과 재주문을 협의합니다.", "공통 원칙: 표시·광고 문구와 효능 주장은 국가별 규정 및 현지 시험 결과를 확인한 뒤 확정합니다."], [["구분", "진입 제품", "영업 순서와 전환 지표"], ["국내", "20% 표준품·CoA·OEM 5~20%", "규격서·샘플 → 유료 시험 → 배합 검토 → 재주문\n지표: 시험 착수·유료전환·재주문율"], ["해외", "영문 규격서·CoA·수출 샘플", "규제 검토 → 파트너 선별 → 현지 시험 → MOQ 협의\n지표: 검토 완료국·계약·재주문 물량"]])+[PageBreak()]
story += page("한 문장으로 설명하면", "02 · thesis", ["가바크루드는 GABA 20% 기준 원료로 공급하고, 가바케어믹스는 가바크루드와 미네랄매트릭스를 결합한 축종별 배합사료로 검증합니다.", "핵심은 효능을 먼저 단정하는 것이 아니라, 제품 규격·축종별 시험·원가·반복 주문을 한 인덱스에서 연결하는 것입니다."])+[PageBreak()]
story += page("두 개의 사업 트랙", "02 · business model", ["원료 사업은 재고와 OEM을 조합해 고객의 농도 요구에 대응합니다. 배합사료 사업은 축종별 생산주기에 맞춘 시험과 현장 성과를 통해 브랜드 축산으로 확장합니다."], [["트랙", "제품", "고객에게 제공하는 가치"], ["가바크루드", "GABA 20% 기준품 · OEM 5~20%", "규격이 명확한 원료 공급과 주문형 농도 대응"], ["가바케어믹스", "가바크루드 + 미네랄매트릭스", "축종별 배합 설계와 생산성·품질 검증"]])+[PageBreak()]
story += page("가바크루드 기준 규격", "03 · crude", ["GABA 20%를 기준으로 설계한 원료입니다. 실제 출하 규격은 로트별 CoA, 안정성, 건조 수율과 품목 분류 확인 후 확정합니다.", "기대효과: 규격이 선명한 원료 선택, 농도별 OEM 대응, 로트·CoA 기반 구매 검토. 효능이 아닌 구매·공급 편의에 대한 마케팅 표현입니다.", "시험 확인 필요: 스트레스 관리, 사료 효율·증체율, 출하 시기, 폐사·이상반응, 육질, 메탄 배출 저감."], [["항목", "기준", "검증 조건"], ["GABA 함량", "20% (w/w)", "로트별 공인시험 또는 CoA"], ["OEM 범위", "5~20%", "고객 발주서와 생산 배치기록"], ["표준품 원가", "7,000원/kg", "사용자 제공 기준·실제 제조원가 확인"]])+[PageBreak()]
story += page("가바케어믹스의 검증 설계", "04 · care mix", ["사료 1톤당 가바케어믹스 1kg을 투입하고, 최종 사료 기준 GABA 100mg/kg을 설계합니다. 따라서 가바케어믹스 1kg에는 GABA 100g, 즉 GABA 10%가 필요합니다.", "GABA 20% 가바크루드 50%와 미네랄매트릭스 50%를 혼합합니다. 표준품 단가 기준 원료 투입원가는 5,000원/kg입니다: 가바크루드 0.5kg×7,000원/kg + 미네랄매트릭스 0.5kg×3,000원/kg. 제조·검사·포장·수율손실은 별도 반영합니다.", "기대효과는 축종별 생산주기에 맞춘 생산성·사료효율·축산물 품질 검증입니다. 메탄가스 저감은 반추위동물 별도 대조시험에서 확인합니다."], [["항목", "설계 기준", "산식·검증 조건"], ["투입량", "사료 1톤당 1kg", "미네랄매트릭스 배합사료 투입 기준"], ["최종 사료 GABA", "100mg/kg", "사료 1톤당 GABA 100g"], ["혼합비", "가바크루드 50% + 미네랄매트릭스 50%", "GABA 20% 가바크루드 기준"], ["원료 투입원가", "5,000원/kg", "사료 1톤당 5,000원 · 최종 매출원가는 별도 확정"]])+[PageBreak()]
story += page("반추위동물 메탄가스 저감 검증", "05 · future business", ["이 프로젝트는 비육우·젖소·염소·면양에서 가바케어믹스 적용군과 대조군의 메탄 배출량과 생산성 지표를 함께 확인하는 별도 사업 검증입니다.", "시장성은 저메탄 사료 수요를 곧바로 매출로 가정하지 않습니다. 메탄 측정, 축종별 장기 시험, 표시·인증 가능 문구, 사료 1톤당 추가 원가와 농가 경제성이 동시에 확인돼야 사업화합니다.", "OECD·FAO는 사료 고도화와 생산성 개선을 축산 배출 저감 경로 중 하나로 제시합니다. 가바의 메탄 저감 효과와 탄소 성과는 본 프로젝트의 시험 결과가 나온 뒤 판단합니다."], [["검증 단계", "확인할 항목", "사업화 조건"], ["설계", "메탄 측정기관·대조군·사료섭취량", "연구기관 시험계획 승인"], ["본시험", "메탄 배출량·증체·산유·사료효율", "축종별 생산주기 종료 성적"], ["사업화", "표시·인증·경제성·유료 고객", "규정 서면 확인과 반복 주문"]])+[PageBreak()]
story += page("공급 기반과 CAPA", "05 · supply", ["생산 파트너의 사용자 제공 CAPA를 배양액과 가바(20%)크루드 이론 생산량으로 병행 관리합니다."], [["파트너", "배양액 CAPA", "가바(20%)크루드 이론 CAPA"], ["비전바이오켐", "월 20톤", "월 20톤"], ["지에프퍼멘텍", "월 200톤", "월 200톤"], ["합계", "월 220톤", "월 220톤"]])+[PageBreak()]
story += page("사업화 핵심 멤버", "06 · team", ["분석, 시험·검사, 정밀발효·정제 역량을 연결해 제품 규격과 축종별 검증을 함께 추진합니다."], [["구분", "핵심 멤버", "주요 경력"], ["분석기술 전문가", "장순욱 · 셀핀다 생명과학연구소 부사장", "전 해원바이오 전무 · 전 한국신약 연구소장"], ["분석기술 고문", "구자룡 · 충남대 농업과학연구소 총괄책임", "전 우성사료 연구소장"], ["정밀발효·정제 전문가", "박지호 · 셀핀다 생명과학연구소 소장", "전 현대바이오랜드 재직"]])+[PageBreak()]
story += page("준비도 41점에서 100점까지", "07 · readiness", ["현재 점수는 확인된 증빙만 반영한 41점입니다. 남은 59점은 자료를 모았다는 사실만으로 올리지 않고, 검토 결론과 계약·시험·원가 자료가 연결될 때 단계적으로 반영합니다."], [["축", "남은 점수", "필요한 증빙"], ["규제·품목분류", "+14", "분류·등록 경로·표시 문구 서면 확인"], ["제품·유효용량", "+12", "규격·안정성·6개 축종 시험"], ["공급·경제성·상업성", "+33", "OEM·실제 원가·유료 반복주문"]])+[PageBreak()]
story += page("자동 수집은 검토를 돕는 운영 장치", "07 · evidence operations", ["연구 자료·논문·국내 동향·해외 동향을 정기 수집합니다. 자동 수집 자료는 원문·기준일·축종·시험조건을 확인하기 전까지 검토 대기로 유지합니다.", "공개 인덱스에서 자료의 출처와 검토 상태를 함께 확인할 수 있습니다."])+[PageBreak()]
story += page("투자자와 사료업체가 확인할 질문", "08 · decision", ["첫째, 제품 규격이 로트별로 재현되는가. 둘째, 축종별 시험기간과 판정지표가 충분한가. 셋째, 실제 매출원가와 반복 주문이 확인되는가.", "이 세 질문에 연결된 증빙이 쌓일수록 준비도 점수와 사업 확장 속도를 함께 높일 수 있습니다."])+[PageBreak()]
story += page("APPENDIX · 용어와 주의사항", "appendix", ["CAPA: 정해진 기간에 생산할 수 있는 최대 물량. 이 자료의 크루드 CAPA는 배양액 1톤당 이론 생산량 1톤으로 계산한 값이며, 실제 수율로 보정해야 합니다.", "CoA: 시험성적서. OEM: 주문자 상표 부착 생산. FCR: 체중 1kg 증가에 필요한 사료량.", "본 문서는 사업 검토용 자료이며, 법률·수의·사료·투자 전문 자문을 대신하지 않습니다."])

SimpleDocTemplate(str(OUT), pagesize=PAGE, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title="가바 사료 비즈니스 모델 스피치덱").build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
