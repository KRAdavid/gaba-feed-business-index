# GABA 사료 비즈니스 모델 인덱스

사료 업계 경험이 없는 사용자도 사업 구조, 준비도, 검증 과제, 정책·연구·원료시장 동향을 한 화면에서 이해하도록 만든 공개 인덱스입니다.

## 사업 구조

- **가바크루드:** GABA 20% 기준품과 OEM 5~20% 맞춤 농도의 원료 판매 사업
- **가바케어믹스:** 가바크루드와 미네랄매트릭스를 조합한 배합사료 사업

두 사업은 판매 대상과 수익 구조가 다르지만, 규제 검토·성분 분석·로트 품질·공급 조건·고객 시험은 같은 기준으로 관리합니다.

## 공개 화면

서비스 주소: [https://gaba-feed-business-index.dubaissday.chatgpt.site](https://gaba-feed-business-index.dubaissday.chatgpt.site)

공개 화면은 매주 월요일 오전에 정책·연구·원료시장 자료를 다시 확인합니다. 외부 자료를 받지 못하면 직전 자료를 유지하고 화면에 자료 상태를 알립니다. 자동 수집 자료는 검토 대기 항목으로 표시하며, 전문가가 확인하기 전에는 준비도 점수에 반영하지 않습니다.

## 핵심 산출물

- `GABA_Index_Master.xlsx`: 준비도, 근거 자료, 손익 가정, 사업 구조, 핵심 인력, 생산 파트너를 관리하는 원본
- `GABA_Business_Model_Index.html`: 회의와 내부 공유에 쓰는 휴대형 인덱스
- `GABA_Feed_Business_Model_Speech_Deck_v1.pptx`: 사료업체·투자자 대상 20장 발표자료
- `GABA_Index_Artifact.json`: 휴대형 인덱스를 다시 만들 수 있는 구조화 원본

## 로컬 실행

```powershell
python scripts/update_public_index.py
python scripts/localize_portable_artifact.py
python scripts/audit_korean_copy.py
python scripts/validate_public_index.py
python scripts/prepare_public_site.py
python -m http.server 8000 --directory docs
```

브라우저에서 `http://localhost:8000`을 엽니다. `index.html`을 파일로 직접 열면 브라우저 보안 정책 때문에 JSON 자료를 불러오지 못할 수 있습니다.

## 자료 관리 원칙

- 사용자 제공 이력과 생산가능량은 외부 확인 전까지 ‘사용자 제공 자료’로 표시합니다.
- 비전바이오켐 20톤/월과 지에프퍼멘텍 200톤/월은 배양액 생산가능량입니다. 계약, 실제 가동, 품질 체계를 확인한 뒤 공급계획에 반영합니다.
- 가격·원가·투입량·고객가치는 검증 전 가정과 실제 확인값을 구분합니다.
- 규제 분류, 표시·광고 문구, 축종별 유효용량은 관계기관·전문가·공인 시험기관에서 별도로 확인합니다.
- 모든 공개 자료의 마지막 페이지 또는 마지막 구역은 `APPENDIX`로 유지합니다.

## 주요 파일

- `data/base_index.json`: 사업 정의, 준비도, 검증 과제, 인력, 생산 파트너, 용어
- `data/manual_signals.json`: 담당자가 확인한 정책·연구·시장 자료
- `docs/data/index.json`: 공개 화면이 읽는 최신 스냅샷
- `scripts/update_public_index.py`: 외부 자료 수집과 스냅샷 생성
- `scripts/audit_korean_copy.py`: 어색한 번역투와 금지 표현 검사
- `scripts/validate_public_index.py`: 데이터 구조와 핵심 수치 검사
- `scripts/validate_public_site.py`: 공개 화면의 필수 구역과 다운로드 파일 검사
- `KOREAN_COPY_AUDIT.md`: 최종 문장 감리 기록

## Appendix · 이용 안내

이 인덱스는 사업 준비도 관리 도구이며 법률·수의·사료·투자 자문을 대신하지 않습니다. 품목 분류, 표시·광고, 제품 효능과 안전성, 공장 적합성, 실제 경제성은 관계기관과 전문가, 공인 시험기관, 실제 견적과 고객 현장에서 각각 확인해야 합니다.
