#!/usr/bin/env python3
from pathlib import Path
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'docs' / 'downloads' / 'GABA_Crude_Specification_v1.pdf'
FONT_CANDIDATES = [('NanumGothic','/usr/share/fonts/truetype/nanum/NanumGothic.ttf','/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf')]
font_name=bold_name=None
for name,regular,bold in FONT_CANDIDATES:
    if Path(regular).exists() and Path(bold).exists():
        pdfmetrics.registerFont(TTFont(name,regular)); pdfmetrics.registerFont(TTFont(name+'Bold',bold)); font_name=name; bold_name=name+'Bold'; break
if not font_name: raise SystemExit('Install fonts-nanum before generating the PDF.')
GREEN=colors.HexColor('#0B6C4F'); DARK=colors.HexColor('#16382D'); BLUE=colors.HexColor('#155D91'); LIGHT=colors.HexColor('#EAF5EF'); LIGHT_BLUE=colors.HexColor('#EAF3F9'); GRAY=colors.HexColor('#5F7068'); GRID=colors.HexColor('#CCDAD3'); AMBER_BG=colors.HexColor('#FFF8E8'); RED_BG=colors.HexColor('#FFF3F1'); RED=colors.HexColor('#A4423B')
styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name='KBody',fontName=font_name,fontSize=8.7,leading=12.7,textColor=DARK,spaceAfter=4))
styles.add(ParagraphStyle(name='KSmall',fontName=font_name,fontSize=7.2,leading=10.2,textColor=GRAY))
styles.add(ParagraphStyle(name='KTitle',fontName=bold_name,fontSize=28,leading=31,textColor=DARK,spaceAfter=5))
styles.add(ParagraphStyle(name='KSubTitle',fontName=bold_name,fontSize=16,leading=20,textColor=GREEN,spaceAfter=12))
styles.add(ParagraphStyle(name='KH1',fontName=bold_name,fontSize=17,leading=20,textColor=DARK,spaceBefore=4,spaceAfter=8))
styles.add(ParagraphStyle(name='KH2',fontName=bold_name,fontSize=11.5,leading=14,textColor=GREEN,spaceBefore=7,spaceAfter=5))
styles.add(ParagraphStyle(name='KWhite',fontName=bold_name,fontSize=8,leading=10,textColor=colors.white,alignment=1))
styles.add(ParagraphStyle(name='KCell',fontName=font_name,fontSize=7.5,leading=10,textColor=DARK))
styles.add(ParagraphStyle(name='KCellBold',fontName=bold_name,fontSize=7.5,leading=10,textColor=DARK))
styles.add(ParagraphStyle(name='KNote',fontName=font_name,fontSize=8,leading=11.5,textColor=DARK))
styles.add(ParagraphStyle(name='KCenter',fontName=font_name,fontSize=8.5,leading=12,textColor=GRAY,alignment=1))
def P(text,style='KBody'): return Paragraph(text,styles[style])
def header_footer(canvas,doc):
    canvas.saveState(); canvas.setFont(font_name,7); canvas.setFillColor(GREEN); canvas.drawString(18*mm,286*mm,'CELLPINDA  |  GABA FEED SOLUTIONS'); canvas.setFillColor(GRAY); canvas.drawRightString(192*mm,10*mm,f'GABA Crude 20 · v1.0 · {doc.page}'); canvas.restoreState()
def section_title(title,en=''):
    return [P(f'{title} <font color="#6a7a72" size="9">{en}</font>','KH1'),Table([['','']],colWidths=[26*mm,144*mm],rowHeights=[1.5*mm],style=TableStyle([('BACKGROUND',(0,0),(0,0),GREEN),('BACKGROUND',(1,0),(1,0),colors.HexColor('#DCE7E1')),('LEFTPADDING',(0,0),(-1,-1),0),('RIGHTPADDING',(0,0),(-1,-1),0),('TOPPADDING',(0,0),(-1,-1),0),('BOTTOMPADDING',(0,0),(-1,-1),0)])),Spacer(1,4)]
def data_table(headers,rows,widths,header_color=GREEN,first_gray=True):
    data=[[P(h,'KWhite') for h in headers]]+[[P(str(v),'KCellBold' if i==0 else 'KCell') for i,v in enumerate(r)] for r in rows]
    ts=[('BACKGROUND',(0,0),(-1,0),header_color),('GRID',(0,0),(-1,-1),0.35,GRID),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]
    if first_gray: ts.append(('BACKGROUND',(0,1),(0,-1),colors.HexColor('#F3F6F4')))
    return Table(data,colWidths=widths,repeatRows=1,style=TableStyle(ts))
def note(title,body,color=GREEN,bg=LIGHT):
    return Table([[P(title,'KCellBold')],[P(body,'KNote')]],colWidths=[170*mm],style=TableStyle([('BACKGROUND',(0,0),(-1,-1),bg),('BOX',(0,0),(-1,-1),0.8,color),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('TEXTCOLOR',(0,0),(0,0),color)]))
OUT.parent.mkdir(parents=True,exist_ok=True)
doc=SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=17*mm,bottomMargin=16*mm,title='GABA Crude 20 Technical & Commercial Specification',author='Cellpinda Life Science Research Institute')
story=[]
story += [Spacer(1,18*mm),P('CELLPINDA','KH2'),P('GABA CRUDE 20','KTitle'),P('가바크루드 20 기술·사업 사양서','KSubTitle'),P('Fermentation-derived GABA feed ingredient<br/>Technical &amp; Commercial Specification'),Spacer(1,8*mm)]
cover=[('문서 버전','v1.0'),('발행일','2026-08-07'),('문서 상태','사업 검토용 잠정 규격 / Provisional Commercial Specification'),('기준 제품','GABA 20% 기준품 (GABA Crude 20)'),('문의','feed@cellpinda.com')]
story += [data_table(['항목','내용'],cover,[38*mm,132*mm],DARK),Spacer(1,6*mm),note('문서 사용 범위','본 문서는 바이어의 제품 검토, 샘플·파일럿 설계 및 견적 협의를 위한 기술·사업 자료입니다. 최종 상업 규격은 승인된 제조공정, 분석법 검증, 목표국 사료 규정과 상업 생산 로트의 시험성적서(CoA)를 기준으로 확정합니다.'),Spacer(1,7*mm),P('핵심 포지셔닝','KH2'),P('• GABA 20%를 기준으로 관리하는 B2B 사료용 원료<br/>• 프리믹스·완전배합사료·축종별 기능성 제품 개발에 적용<br/>• 효능을 고정하지 않고 축종별 파일럿과 대조시험으로 검증'),PageBreak()]
story += section_title('1. 제품 개요','Product Overview')
summary=[('제품명','Cellpinda GABA Crude 20 / 가바크루드 20'),('제품 분류','사료용 GABA 원료·프리믹스 원료(B2B)'),('주요 성분','Gamma-aminobutyric acid(GABA)'),('제조 개념','발효 유래 GABA를 농축·건조하여 기준 함량으로 표준화'),('기준 함량','GABA 20% 이상 - HPLC, as-is 기준(잠정 내부 규격)'),('주요 용도','프리믹스, 완전배합사료, 축종별 Care Mix, 농장 파일럿'),('표준 포장안','20 kg/bag - 최종 포장·재질은 공급계약서 기준'),('보관','밀봉 상태로 서늘하고 건조한 곳에 보관, 고온·습기·직사광선 회피')]
story += [data_table(['구분','제품 정보'],summary,[38*mm,132*mm]),Spacer(1,6*mm),P('2. 구매자별 적용 경로','KH2')]
buyers=[('사료회사 R&D','배합 적합성, 시험설계, 제품 차별화'),('구매·원료조달','규격, CoA, MOQ, 단가, 납기, 공급안정성'),('농장·비육장','대조군, 기간, KPI와 도입비 대비 현장 변화'),('수입·유통사','국가별 분류, 표시, 영문 기술문서, 공급조건'),('연구기관','용량반응, 안전성, 생산성·품질 데이터')]
story += [data_table(['바이어 유형','우선 검토사항'],buyers,[42*mm,128*mm],BLUE),Spacer(1,5*mm),note('과학적 표현 원칙','돼지 연구에서는 스트레스 행동과 ACTH·cortisol 감소, 일부 연구에서 ADG·건물소화율 개선이 보고되었습니다. 그러나 연구조건에 따라 ADG·섭취량 유의차가 없었던 결과도 있으므로 성장·FCR·번식성적은 확정효능으로 표시하지 않고 대조시험으로 확인합니다.',colors.HexColor('#A86F12'),colors.HexColor('#FFF8E8')),PageBreak()]
story += section_title('3. 잠정 제품 규격','Provisional Product Specification')
spec=[('GABA 함량','≥20.0%(w/w)','HPLC','상업 로트 CoA 필수'),('성상','분말','육안','승인 표준시료 기준 확정'),('수분','로트별 보고','건조감량/승인법','상업 3개 로트 후 한계 확정'),('pH','요청 시 보고','승인 농도 수용액','시험조건 CoA 명시'),('입도','고객 규격 협의','체분석','혼합공정에 맞춰 확정'),('일반세균·효모·곰팡이','목표국 기준 적합','공인법','정기 또는 로트 시험'),('Salmonella / E. coli','목표국 기준 적합','공인법','위해미생물 관리'),('Pb·As·Cd·Hg','목표국 기준 적합','ICP 계열','원료·완제품 주기 검증'),('이물·금속','부적합 이물 없음','공정관리','체·자석·금속검출')]
story += [data_table(['시험 항목','잠정 기준','시험방법','관리 원칙'],spec,[34*mm,43*mm,40*mm,53*mm]),Spacer(1,5*mm),note('중요','GABA ≥20.0% 외의 수치형 한계는 현재 제공자료만으로 확정하지 않았습니다. 수분·미생물·중금속·입도·유통기한은 상업 제조공정, 최초 3개 로트 분석과 목표국 규정을 반영해 최종 승인합니다.',RED,RED_BG),Spacer(1,6*mm),P('4. CoA 및 공급 문서','KH2')]
docrows=[('필수','제품 규격서, 로트별 CoA, 포장·보관 조건, 제조일·로트 추적'),('품질 요청','미생물, 중금속, 수분, 입도, 안정성·보존시험 요약'),('수출 요청','원산지, 제조공정 요약, SDS, GMO·알레르겐·BSE/TSE 해당 선언'),('규제 검토','목표국 분류와 표시·효능문구는 현지 검토 후 확정')]
story += [data_table(['자료 구분','제공 범위'],docrows,[38*mm,132*mm],BLUE),PageBreak()]
story += section_title('5. 배합량 환산 가이드','Inclusion Conversion Guide')
story += [P('가바크루드 20의 사료 1톤당 투입량은 아래 식으로 계산합니다.'),note('계산식','가바크루드 투입량(kg/사료톤) = 목표 GABA 농도(mg/kg) ÷ 200<br/>예: 목표 GABA 100 mg/kg → 가바크루드 20을 0.50 kg/사료톤 투입',BLUE,LIGHT_BLUE),Spacer(1,5*mm)]
conv=[]
for ppm in [30,50,75,100,150,500]:
    inc=ppm/200; conv.append((f'{ppm} mg/kg',f'{inc:.3f} kg/t',f'{inc*1000:.0f} g/t',f'{inc*18000:,.0f}원/t'))
story += [data_table(['목표 GABA','가바크루드 20','그램 환산','참고 원료비*'],conv,[38*mm,45*mm,42*mm,45*mm]),P('* 18,000원/kg 가정, VAT·운송·혼합·포장비 제외. 실제 공급가는 견적서 기준입니다.','KSmall'),Spacer(1,4*mm),P('6. 시험설계용 범위 예시','KH2')]
pilot=[('이유·육성돈','30, 50, 500 mg/kg 연구 사례','ADG·ADFI·FCR·소화율·행동·cortisol'),('씨돼지','고온기 4~8주 파일럿','섭취·체중·cortisol·정액 KPI'),('한우·육우·와규','50~150 mg/kg 단계 검토','DMI·ADG·FCR·육색·TBARS·등급'),('육계','50~100 mg/kg 파일럿','BWG·FCR·폐사·H/L·TBARS')]
story += [data_table(['대상','시험설계 참고','권장 KPI'],pilot,[35*mm,58*mm,77*mm],BLUE),Spacer(1,5*mm),note('배합 실무','투입량이 적으므로 직접 투입보다 단계희석 또는 프리믹스 방식으로 혼합균일도를 확보합니다. 혼합시간, 투입순서, 펠릿·열공정 안정성과 완제품 내 GABA 함량을 확인해야 합니다.'),PageBreak()]
story += section_title('7. 파일럿 및 상업도입 절차','Pilot-to-Commercial Workflow')
flow=[('01 조건 확인','축종·기초사료·목표농도·기간·KPI 확인'),('02 규격·샘플','잠정 규격·대표 CoA 검토와 샘플 제공'),('03 파일럿','대조군·급여량·기록주기·중단기준 합의'),('04 시험·모니터링','섭취·건강·생산성·스트레스·품질 기록'),('05 경제성','사료비·도입비·생산성·품질·재현성 분석'),('06 상업 전환','최종 규격·MOQ·단가·포장·납기 확정')]
story += [data_table(['단계','실행 내용'],flow,[36*mm,134*mm]),Spacer(1,6*mm),P('8. 상업조건 체크리스트','KH2'),P('• GABA 20% 기준품 또는 5~20% 주문형 농도<br/>• 샘플·초도·연간 예상 물량과 납품지역<br/>• 표준 또는 고객 지정 포장<br/>• CoA·SDS·원산지·제조공정·품질 선언서<br/>• MOQ·리드타임·결제·운송 조건<br/>• 국가별 분류·표시·효능문구 검토 책임'),Spacer(1,5*mm),note('표현 및 규제 주의','본 제품은 사료용 원료입니다. 구체적 스트레스·성장·번식·메탄저감 주장은 국가별 규정과 완제품·현장 시험결과에 따라 추가 검토가 필요합니다. 메탄저감·탄소배출권 효과는 현재 사양으로 확정하지 않습니다.',colors.HexColor('#A86F12'),colors.HexColor('#FFF8E8')),Spacer(1,8*mm),P('9. 근거 요약','KH2'),P('• 돼지 30 mg/kg: 공격행동 감소, GH 증가, ACTH·cortisol 감소; ADG·ADFI 유의차 없음.<br/>• 육성돈 0.05%: ADG와 건물소화율 증가.<br/>• 씨돼지: 직접 번식효능 근거가 부족하므로 고온기 4~8주 파일럿 권장.<br/>• 한우·육우: 고온 스트레스 조건의 성장·소화율·항산화·육질 관련 결과 보고.<br/>• 와규: 일부 군 시험 후 ADG·FCR·건강·육질·ROI 재평가가 적절.'),Spacer(1,8*mm),P('CELLPINDA GABA FEED SOLUTIONS','KSubTitle'),P('Business inquiry: feed@cellpinda.com','KCenter')]
doc.build(story,onFirstPage=header_footer,onLaterPages=header_footer)
print(OUT)
