#!/usr/bin/env python3
"""Localize the canonical portable artifact's fixed UI labels into Korean."""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path


FIXED_REPLACEMENTS = {
    '<html lang="en"': '<html lang="ko"',
    'Data Analytics dashboard': 'GABA 사업 대시보드',
    'Source for ': '근거: ',
    'Source: ': '출처: ',
    'File: ': '파일: ',
    'Table: ': '테이블: ',
    '>Sources</h2>': '>출처</h2>',
    ' data</caption>': ' 자료</caption>',
    '가바크루드 원료 사업과 비육 한우 브랜드 축산용 배합사료 가바케어믹스의 목표, 검증 일정, KPI, 준비도와 실행 근거를 5분 안에 파악하는 운영 대시보드': '가바크루드 원료 사업과 주요 가축별 가바케어믹스 배합사료의 검증기간, 현재 준비도 41점과 목표 100점의 완료 증빙을 5분 안에 파악하는 운영 대시보드',
    '가바케어믹스는 비육 한우의 육질 개선과 생산성 향상을 목표로 하는 브랜드 축산용 배합사료로 고도화합니다. 30일 안에 제품·사업 준비와 유료 농장 실증을 시작하고, 90일에 생산성 조기 신호를 확인하며, 육질은 출하 성적으로 최종 판단합니다.': '가바케어믹스는 주요 가축의 생산성과 축산물 품질을 목표로 하는 브랜드 배합사료로 고도화합니다. 30일 안에 제품·사업 준비와 유료 시험을 시작하고, 효능은 축종별 35~168일 이상의 본시험과 생산주기 종료 성적으로 판단합니다. 현재 확인된 준비도는 41점이며 목표 100점은 완료 증빙이 검토된 뒤에만 반영합니다.',
    '>준비도 / 100<': '>현재 준비도 / 100<',
    '100점 만점의 현재 준비도입니다. 원문 검토를 마친 근거가 있을 때만 점수를 올립니다.': '확인된 증빙만 반영한 현재 준비도입니다. 목표 100점과 분리해 표시합니다.',
    '>유료 실증 착수<': '>유료 시험 착수<',
    '제품 규격, 시험생산, 원가와 유료 농장 실증을 시작하는 목표 기간입니다.': '제품 규격, 시험생산, 원가와 우선 축종의 유료 시험을 시작하는 목표 기간입니다.',
    '가바크루드 + 미네랄매트릭스 · 비육 한우 브랜드 축산용 배합': '가바크루드 + 미네랄매트릭스 · 주요 가축별 브랜드 배합',
    '배합사료 판매·유료 농장 실증': '배합사료 판매·유료 연구·농장 실증',
    '활성함량 · 균일도 · 안정성 · 생산성 · 출하 육질': '활성함량 · 균일도 · 안정성 · 축종별 생산성 · 축산물 품질',
    '<td>제품·사업 준비</td><td>규격·시험생산·원가·유료 농장 1곳·발주서 1건</td><td>비육 한우 실증 착수</td>': '<td>공통 착수 준비</td><td>규격·시험생산·실제 원가·우선 축종 유료 시험 계약</td><td>축종별 본시험 착수</td>',
    '<td>90일</td><td>생산성 조기 신호</td><td>섭취량·일당증체량·사료요구율·kg 증체당 사료비</td><td>시험 지속·배합 보정</td>': '<td>35~168일 이상</td><td>축종별 장기 효능시험</td><td>증체·산유·산란·사료효율·안전성</td><td>축종별 지속·보정·중단</td>',
    '<td>출하 시</td><td>육질 최종 평가</td><td>도체중·등심단면적·근내지방도·육질등급·등지방두께</td><td>반복 주문·브랜드 적용</td>': '<td>생산주기 종료</td><td>최종 성과 평가</td><td>도체·육질·우유·계란 품질과 경제성</td><td>반복 주문·브랜드 적용</td>',
    '육질·생산성·사업성·제품 품질을 함께 봅니다': '축산물 품질·생산성·사업성·제품 품질을 함께 봅니다',
    '<td>육질 성과</td><td>도체중·등심단면적·근내지방도·육질등급·등지방두께</td>': '<td>축산물 품질</td><td>도체·육질, 유량·유성분, 산란율·난질</td>',
    '<td>출하 시</td><td>개체 식별이 연결된 도축 성적서</td>': '<td>생산주기 종료</td><td>개체·군 식별이 연결된 최종 성적</td>',
    '<td>일당증체량·사료요구율·kg 증체당 사료비</td>': '<td>증체·산유·산란 성적, 사료효율, 단위 생산량당 사료비</td>',
    '<td>31~90일·출하 시</td><td>개체 체중·급여량·사료비 기록</td>': '<td>축종별 본시험·종료</td><td>생산성·급여량·사료비 기록</td>',
    '<td>비육 한우 농장의 유료 시험과 발주서</td><td>30일 안에 농장 1곳·발주서 1건</td>': '<td>연구기관·농장 계약과 발주서</td><td>30일 안에 우선 축종 유료 시험 1건</td>',
    '<h2>신속 검증 일정</h2>': '<h2>축종별 검증 실행 순서</h2>',
    '<strong>0~7일</strong> — 제품 규격, 품목·표시 문구, 비육 한우 대조군 시험계획 확정': '<strong>0~7일</strong> — 제품 규격과 6개 축종군의 대조군·용량·판정지표·시험기간 확정',
    '<strong>22~30일</strong> — 유료 농장 1곳·발주서 1건을 확보하고 기초 체중·섭취량 기록 시작': '<strong>22~30일</strong> — 우선 축종의 연구기관 또는 농장 계약·발주서 확보',
    '<strong>31~90일</strong> — 일당증체량, 사료요구율, kg 증체당 사료비의 조기 신호 확인': '<strong>축종별 35~168일 이상</strong> — 증체·산유·산란 성적, 사료효율과 안전성 비교',
    '<strong>출하 시</strong> — 도체중, 등심단면적, 근내지방도, 육질등급, 등지방두께로 최종 판단': '<strong>생산주기 종료</strong> — 도체·육질, 우유, 계란 품질과 경제성으로 최종 판단',
    '비육 한우 대조군 시험계획 확정': '6개 축종군의 대조군·용량·판정지표·시험기간 확정',
    '유료 농장 1곳·발주서 1건을 확보하고 기초 체중·섭취량 기록 시작': '우선 축종의 연구기관 또는 농장 계약·발주서 확보',
    '9,240원/kg·4,681.8원/kg 비용 연결': '실제 견적·시험생산 수율·최종 매출원가 연결',
    '근거: 신속 검증 일정': '근거: 축종별 검증 실행 순서',
    '30일 목표는 제품·사업 준비와 유료 실증 착수 시점이며 육질 개선 효능을 확정하는 시점이 아닙니다. 생산성은 90일의 조기 신호와 출하 시점의 누적 결과를 함께 보고, 육질은 개체 식별이 연결된 도축 성적서로 최종 판단합니다.': '30일 목표는 제품·사업 준비와 유료 시험 착수 시점이며 효능을 확정하는 시점이 아닙니다. 생산성과 축산물 품질은 축종별 35~168일 이상의 본시험과 출하·비유·산란주기 종료 결과를 함께 보고 판단합니다. 현재 준비도는 확인된 증빙 기준 41점이며 목표 100점은 모든 완료 증빙이 검토된 뒤에만 반영합니다.',
}

SPECIES_BLOCK = '''<div class="portable-block portable-layout-full" data-artifact-block-id="species_validation" data-artifact-block-type="table" data-layout="full"><section class="portable-content-card portable-table-card" data-artifact-id="species_validation_table" data-artifact-kind="table" data-table-id="species_validation_table"><header class="portable-visual-header"><h2>시험기간은 가축의 생산주기에 맞춥니다</h2></header><div class="portable-table-source-region"><div class="portable-table-scroll"><table><caption>축종별 장기 효능시험 계획 기준</caption><thead><tr><th>축종군</th><th>생산단계</th><th>최소 본시험 기간</th><th>최종 판정</th><th>핵심 지표</th></tr></thead><tbody><tr><td>비육우</td><td>비육기</td><td>168일 이상</td><td>출하·도축 시</td><td>ADG·FCR·도체·육질·사료비</td></tr><tr><td>젖소</td><td>착유우</td><td>84일 이상</td><td>전체 비유기 함께 보고</td><td>산유량·유성분·사료효율·건강</td></tr><tr><td>돼지</td><td>이유자돈·비육돈</td><td>42일 · 70일 이상</td><td>비육돈은 출하 시</td><td>ADG·FCR·출하일령·도체</td></tr><tr><td>육계</td><td>부화 후 출하기</td><td>35일</td><td>출하·도축 시</td><td>증체·FCR·폐사율·도체수율</td></tr><tr><td>산란계</td><td>산란기</td><td>168일</td><td>시험 산란주기 종료</td><td>산란율·난중·FCR·난질</td></tr><tr><td>염소·면양</td><td>육성·비육·착유</td><td>56일 이상 · 착유 84일</td><td>출하 또는 비유기 종료</td><td>증체·FCR·도체 또는 유량·유성분</td></tr></tbody></table></div></div><p class="portable-table-note">EU 집행규정 429/2008 부속서 IV 기준 · 국내 연구기관이 세부 설계 확정</p></section></div>'''

READINESS_TARGET_BLOCK = '''<div class="portable-block portable-layout-full" data-artifact-block-id="readiness_target" data-artifact-block-type="markdown" data-layout="full"><section class="portable-markdown"><h2>41점에서 100점까지</h2><p><strong>현재 확인 41점 → 증빙 확보 +59점 → 목표 100점</strong></p><ul><li>규제 +14점: 품목 분류·등록 경로·사용조건·표시 문구</li><li>제품 +12점: 제품 규격·안정성·6개 축종군 시험 결과</li><li>공급 +8점: OEM 실사·품질협약·CAPA·MOQ·납기·회수</li><li>단위 경제성 +9점: 실제 견적·수율·매출원가·매출총이익</li><li>상업성 +16점: 유료 시험·실제 매출·반복 발주</li></ul><p>파일·URL·기준일·검토 결론이 연결될 때만 점수를 올립니다.</p></section></div>'''

COLLECTION_BLOCK = '''<div class="portable-block portable-layout-full" data-artifact-block-id="collection_categories" data-artifact-block-type="table" data-layout="full"><section class="portable-content-card portable-table-card" data-artifact-id="collection_categories_table" data-artifact-kind="table" data-table-id="collection_categories_table"><header class="portable-visual-header"><h2>연구 자료·논문·시장 동향 수집</h2></header><div class="portable-table-scroll"><table><caption>공개 자료 수집 카테고리</caption><thead><tr><th>카테고리</th><th>수집 대상</th><th>갱신 주기</th><th>검토 원칙</th><th>연결 출처</th></tr></thead><tbody><tr><td>연구 자료</td><td>축종별 생산성·품질·안전성 연구</td><td>주 1회</td><td>원문·축종·용량·시험기간 확인 후 반영</td><td>4개</td></tr><tr><td>논문</td><td>GABA와 사료·축산 동료심사 논문</td><td>주 1회</td><td>논문 존재와 제품 효능 주장을 구분</td><td>3개</td></tr><tr><td>시장 동향</td><td>정책·산업 변화·원료 가격</td><td>주 1회·월 1회</td><td>출처·기준월 확인 후 준비도와 분리</td><td>3개</td></tr></tbody></table></div><p class="portable-table-note">자동 수집 자료는 검토 대기로 표시되며 준비도 점수에 자동 반영되지 않습니다.</p></section></div>'''


def localize_time(match: re.Match[str]) -> str:
    raw = match.group(1)
    try:
        utc_time = datetime.fromisoformat(raw.replace('Z', '+00:00'))
    except ValueError:
        return match.group(0)
    korea_time = utc_time.astimezone(timezone(timedelta(hours=9)))
    label = f'{korea_time.year}년 {korea_time.month}월 {korea_time.day}일 {korea_time:%H:%M} (한국 시간)'
    return f'<time datetime="{raw}">{label}</time>'


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('html', nargs='?', default='GABA_Business_Model_Index.html')
    args = parser.parse_args()

    path = Path(args.html).resolve()
    content = path.read_text(encoding='utf-8-sig')
    for source, target in FIXED_REPLACEMENTS.items():
        content = content.replace(source, target)
    species_anchor = '<div class="portable-block portable-layout-full" data-artifact-block-id="caremix_kpis"'
    if 'data-artifact-block-id="species_validation"' not in content and species_anchor in content:
        content = content.replace(species_anchor, SPECIES_BLOCK + species_anchor, 1)
    readiness_anchor = '<div class="portable-block portable-layout-full" data-artifact-block-id="signals"'
    if 'data-artifact-block-id="readiness_target"' not in content and readiness_anchor in content:
        content = content.replace(readiness_anchor, READINESS_TARGET_BLOCK + readiness_anchor, 1)
    collection_anchor = '<div class="portable-block portable-layout-full" data-artifact-block-id="signals"'
    if 'data-artifact-block-id="collection_categories"' not in content and collection_anchor in content:
        content = content.replace(collection_anchor, COLLECTION_BLOCK + collection_anchor, 1)
    content = re.sub(
        r'<p><strong><span class="portable-source-tooltip portable-source-value"[^>]*>.*?'
        r'<span class="portable-source-value-text">31</span>.*?</span>~90일</strong> — '
        r'일당증체량, 사료요구율, kg 증체당 사료비의 조기 신호 확인</p>',
        '<p><strong>축종별 35~168일 이상</strong> — 증체·산유·산란 성적, 사료효율과 안전성 비교</p>',
        content,
        flags=re.DOTALL,
    )
    content = re.sub(r'<time datetime="([^"]+)">.*?</time>', localize_time, content, count=1)
    forbidden = ['9,240원/kg', '비육 한우 대조군 시험계획', '~90일</strong> — 일당증체량']
    remaining = [term for term in forbidden if term in content]
    if remaining:
        raise ValueError(f'portable artifact still contains stale terms: {remaining}')
    path.write_text(content, encoding='utf-8')
    print(f'localized {path}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
