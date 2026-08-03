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
pdfmetrics.registerFont(TTFont(FONT, r"C:\Windows\Fonts\NotoSans-Regular.ttf"))
pdfmetrics.registerFont(TTFont(FONT + "-Bold", r"C:\Windows\Fonts\NotoSans-Bold.ttf"))

PAGE = landscape(A4)
styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Title"], fontName=FONT+"-Bold", fontSize=28, leading=36, textColor=colors.HexColor("#101828"), spaceAfter=12)
subtitle = ParagraphStyle("subtitle", parent=styles["Normal"], fontName=FONT, fontSize=14, leading=22, textColor=colors.HexColor("#475467"))
head = ParagraphStyle("head", parent=styles["Heading2"], fontName=FONT+"-Bold", fontSize=21, leading=28, textColor=colors.HexColor("#101828"), spaceAfter=14)
body = ParagraphStyle("body", parent=styles["BodyText"], fontName=FONT, fontSize=12, leading=19, textColor=colors.HexColor("#344054"), spaceAfter=8)
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
story += page("한 문장으로 설명하면", "01 · thesis", ["가바크루드는 GABA 20% 기준 원료로 공급하고, 가바케어믹스는 가바크루드와 미네랄매트릭스를 결합한 축종별 배합사료로 검증합니다.", "핵심은 효능을 먼저 단정하는 것이 아니라, 제품 규격·축종별 시험·원가·반복 주문을 한 인덱스에서 연결하는 것입니다."])+[PageBreak()]
story += page("두 개의 사업 트랙", "02 · business model", ["원료 사업은 재고와 OEM을 조합해 고객의 농도 요구에 대응합니다. 배합사료 사업은 축종별 생산주기에 맞춘 시험과 현장 성과를 통해 브랜드 축산으로 확장합니다."], [["트랙", "제품", "고객에게 제공하는 가치"], ["가바크루드", "GABA 20% 기준품 · OEM 5~20%", "규격이 명확한 원료 공급과 주문형 농도 대응"], ["가바케어믹스", "가바크루드 + 미네랄매트릭스", "축종별 배합 설계와 생산성·품질 검증"]])+[PageBreak()]
story += page("가바크루드 기준 규격", "03 · crude", ["GABA 20%를 기준으로 설계한 원료입니다. 실제 출하 규격은 로트별 CoA, 안정성, 건조 수율과 품목 분류 확인 후 확정합니다.", "기대효과: 규격이 선명한 원료 선택, 농도별 OEM 대응, 로트·CoA 기반 구매 검토. 효능이 아닌 구매·공급 편의에 대한 마케팅 표현입니다.", "시험 확인 필요: 스트레스 관리, 사료 효율·증체율, 출하 시기, 폐사·이상반응, 육질, 메탄 배출 저감."], [["항목", "기준", "검증 조건"], ["GABA 함량", "20% (w/w)", "로트별 공인시험 또는 CoA"], ["OEM 범위", "5~20%", "고객 발주서와 생산 배치기록"], ["표준품 원가", "7,000원/kg", "사용자 제공 기준·실제 제조원가 확인"]])+[PageBreak()]
story += page("가바케어믹스의 검증 설계", "04 · care mix", ["가바케어믹스는 제품 1kg에 GABA 100mg을 포함하는 설계안으로, 축종별 실제 섭취량과 유효용량을 시험합니다.", "구성 원가는 가바크루드 표준품 4,000원/kg과 미네랄매트릭스 3,000원/kg을 적용해 7,000원/kg으로 계산합니다.", "기대효과: 축종별 생산주기에 맞춘 브랜드 축산 솔루션, 생산성·사료효율·축산물 품질을 함께 관리하는 시험 프레임, 농장 데이터와 연구기관 검증을 연결하는 재구매 판단 구조.", "시험 확인 필요: 스트레스 지표, 사료 효율·증체율, 출하 시기 단축, 폐사량, 육질, 메탄가스 배출량."], [["축종군", "관찰기간 기준", "핵심 지표"], ["비육우", "168일 이상", "일당증체량·사료요구율·도체성적"], ["젖소", "84일 이상", "산유량·유성분·건물섭취량"], ["돼지·육계·산란계", "42~168일", "증체·사료요구율·출하·산란 지표"]])+[PageBreak()]
story += page("공급 기반과 CAPA", "05 · supply", ["생산 파트너의 사용자 제공 CAPA를 배양액과 가바(20%)크루드 이론 생산량으로 병행 관리합니다."], [["파트너", "배양액 CAPA", "가바(20%)크루드 이론 CAPA"], ["비전바이오켐", "월 20톤", "월 20톤"], ["지에프퍼멘텍", "월 200톤", "월 200톤"], ["합계", "월 220톤", "월 220톤"]])+[PageBreak()]
story += page("준비도 41점에서 100점까지", "06 · readiness", ["현재 점수는 확인된 증빙만 반영한 41점입니다. 남은 59점은 자료를 모았다는 사실만으로 올리지 않고, 검토 결론과 계약·시험·원가 자료가 연결될 때 단계적으로 반영합니다."], [["축", "남은 점수", "필요한 증빙"], ["규제·품목분류", "+14", "분류·등록 경로·표시 문구 서면 확인"], ["제품·유효용량", "+12", "규격·안정성·6개 축종 시험"], ["공급·경제성·상업성", "+33", "OEM·실제 원가·유료 반복주문"]])+[PageBreak()]
story += page("자동 수집은 검토를 돕는 운영 장치", "07 · evidence operations", ["연구 자료·논문·국내 동향·해외 동향을 정기 수집합니다. 자동 수집 자료는 원문·기준일·축종·시험조건을 확인하기 전까지 검토 대기로 유지합니다.", "공개 인덱스에서 자료의 출처와 검토 상태를 함께 확인할 수 있습니다."])+[PageBreak()]
story += page("투자자와 사료업체가 확인할 질문", "08 · decision", ["첫째, 제품 규격이 로트별로 재현되는가. 둘째, 축종별 시험기간과 판정지표가 충분한가. 셋째, 실제 매출원가와 반복 주문이 확인되는가.", "이 세 질문에 연결된 증빙이 쌓일수록 준비도 점수와 사업 확장 속도를 함께 높일 수 있습니다."])+[PageBreak()]
story += page("APPENDIX · 용어와 주의사항", "appendix", ["CAPA: 정해진 기간에 생산할 수 있는 최대 물량. 이 자료의 크루드 CAPA는 배양액 1톤당 이론 생산량 1톤으로 계산한 값이며, 실제 수율로 보정해야 합니다.", "CoA: 시험성적서. OEM: 주문자 상표 부착 생산. FCR: 체중 1kg 증가에 필요한 사료량.", "본 문서는 사업 검토용 자료이며, 법률·수의·사료·투자 전문 자문을 대신하지 않습니다."])

SimpleDocTemplate(str(OUT), pagesize=PAGE, rightMargin=18*mm, leftMargin=18*mm, topMargin=16*mm, bottomMargin=18*mm, title="가바 사료 비즈니스 모델 스피치덱").build(story, onFirstPage=footer, onLaterPages=footer)
print(OUT)
