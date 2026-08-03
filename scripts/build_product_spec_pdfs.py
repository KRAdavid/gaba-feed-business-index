from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
FONT = "NotoSansKR"
pdfmetrics.registerFont(TTFont(FONT, r"C:\Windows\Fonts\malgun.ttf"))
pdfmetrics.registerFont(TTFont(FONT+"-Bold", r"C:\Windows\Fonts\malgunbd.ttf"))
styles = getSampleStyleSheet()
title = ParagraphStyle("title", parent=styles["Title"], fontName=FONT+"-Bold", fontSize=24, leading=32, textColor=colors.HexColor("#101828"))
head = ParagraphStyle("head", parent=styles["Heading2"], fontName=FONT+"-Bold", fontSize=17, leading=24, textColor=colors.HexColor("#101828"))
body = ParagraphStyle("body", parent=styles["BodyText"], fontName=FONT, fontSize=11, leading=18, textColor=colors.HexColor("#344054"), spaceAfter=8)
small = ParagraphStyle("small", parent=body, fontSize=8.5, leading=13, textColor=colors.HexColor("#667085"))

def P(x, s=body): return Paragraph(x, s)
def footer(canvas, doc):
    canvas.saveState(); canvas.setStrokeColor(colors.HexColor("#D0D5DD")); canvas.line(18*mm, 14*mm, 192*mm, 14*mm)
    canvas.setFont(FONT, 8); canvas.setFillColor(colors.HexColor("#667085")); canvas.drawString(18*mm, 8*mm, "GABA 제품 사양서 | 사업 검토용"); canvas.drawRightString(192*mm, 8*mm, str(doc.page)); canvas.restoreState()
def make(path, name, definition, rows, notes):
    story=[P(name,title), P("사업 검토용 기준안 · 출하 규격은 시험성적서와 품목 검토 후 확정", small), Spacer(1,8*mm), P("제품 정의",head), P(definition)]
    table=Table([[P(str(c),small) for c in r] for r in [["항목","기준","확인 방식"]]+rows], colWidths=[42*mm,62*mm,78*mm])
    table.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),colors.HexColor("#E8F5F0")),("GRID",(0,0),(-1,-1),.4,colors.HexColor("#D0D5DD")),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),7),("RIGHTPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),6),("BOTTOMPADDING",(0,0),(-1,-1),6)]))
    story += [table, Spacer(1,8*mm), P("검증 및 사용 주의",head)] + [P(n) for n in notes] + [Spacer(1,5*mm), P("APPENDIX · 용어",head), P("CoA: 시험성적서. OEM: 주문자 상표 부착 생산. 표준품: 품질과 농도의 기준이 되는 제품.")]
    SimpleDocTemplate(str(path), pagesize=A4, rightMargin=18*mm,leftMargin=18*mm,topMargin=18*mm,bottomMargin=20*mm,title=name).build(story,onFirstPage=footer,onLaterPages=footer)

make(ROOT/"GABA_Crude_Specification_v1.pdf", "가바크루드 20% 표준품 사양서", "가바크루드는 GABA 20%를 기준으로 설계한 원료 제품입니다. 고객 요청에 따라 5~20% 농도 OEM을 별도 협의합니다.", [["GABA 함량","20% (w/w)","로트별 CoA"],["표준품 원가","7,000원/kg","사용자 제공 기준·실제 원가 확인"],["원료 사업","기준품·주문형 OEM","발주서·배치기록"]], ["실제 출하 규격은 활성함량, 안정성, 건조 수율, 품목 분류와 표시 문구 검토 후 확정합니다.", "기대효과로 언급되는 스트레스·사료효율·증체·육질·메탄 관련 내용은 축종별 시험으로 확인하기 전까지 효능을 확정하지 않습니다."])
make(ROOT/"GABA_Caremix_Specification_v1.pdf", "가바케어믹스 사양서", "가바케어믹스는 가바크루드와 미네랄매트릭스를 조합한 축종별 배합사료 설계안입니다.", [["GABA 설계량","가축 1마리·1회 50~100mg","가바크루드 20% 기준·축종별 시험"],["이론 원가","약 3,000.25~3,000.50원/kg","가바크루드 0.25~0.50g + 미네랄매트릭스 잔량"],["적용 축종","소·돼지·육계·산란계·염소·면양","대조군 시험·생산주기 종료 판정"]], ["50~100mg은 사용자 제공 설계 범위이며, 실제 유효용량과 급여량은 축종별 시험과 연구기관 검토 후 확정합니다.", "스트레스, 사료효율, 증체율, 출하시기, 폐사량, 육질, 메탄가스 저감은 모두 기대 방향이며 시험 결과로 확인합니다."])
print("created product PDFs")
