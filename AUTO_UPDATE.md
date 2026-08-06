# GABA Feed Intelligence 자동 업데이트 구조 v2

## 목적

`KRAdavid/gaba-feed-business-index`의 공개 대시보드에 사료용 GABA 관련 연구, 정책·규제, 통계 및 시장 자료를 자동으로 갱신하되, 검색어만 우연히 포함된 자료나 미래 연도 오류가 자동 공개되지 않도록 보수적으로 운영합니다.

## 실행 주기

- 매일 03:20 KST: GitHub Actions 예약 실행
- 수동 실행: GitHub → Actions → **Auto-update GABA feed intelligence** → **Run workflow**
- 엔진·설정 변경: `main` 병합 직후 자동 실행
- Pull Request: 네트워크 수집 없이 코드 컴파일, 단위시험 및 설정 JSON 검증

## 데이터 흐름

```text
검증된 기본자료(curated)
        +
PubMed / Europe PMC / Crossref
        +
공식기관 페이지 변경 감시
        ↓
관련성·날짜·식별자·출처 품질검사
        ↓
자동 공개 / 검토 대기 분리
        ↓
GitHub Pages용 JSON 생성
        ↓
변경이 있을 때만 자동 커밋
```

## 수집 소스

### 연구

- PubMed
- Europe PMC
- Crossref
- `config/curated_intelligence.json`의 검증 완료 기본자료

Crossref는 메타데이터 오탐 가능성이 상대적으로 높아 기본적으로 **검토 대기 전용**으로 사용합니다. PubMed와 Europe PMC 자료도 제목·초록에 GABA, 축종, 사료·영양 맥락이 모두 확인되어야 자동 공개됩니다.

### 정책·규제·통계·시장

- 농림축산식품부
- 국가법령정보센터 사료관리법
- EFSA Feed Additives
- U.S. FDA Animal Food
- 호주 APVMA Animal Feed Products
- FAO Animal Production
- OECD-FAO Agricultural Outlook

공식 페이지는 전체 HTML이 아니라 관련 키워드 주변의 정규화된 본문을 비교합니다. 동일한 변경이 2회 연속 확인될 때만 변경 알림을 공개해 날짜·배너·접속 세션 변화에 따른 오경보를 줄입니다.

## 자동 공개 기준

연구자료는 다음 조건을 모두 충족해야 합니다.

1. 제목 또는 초록에 GABA가 명시되어 있음
2. 가축·축종 맥락이 확인됨
3. 사료, 급여, 영양, 소화율 또는 성장성적 맥락이 확인됨
4. DOI 또는 PMID가 있음
5. 발행일이 1990년 이후이고 현재일 기준 허용 범위를 벗어난 미래 연도가 아님
6. PubMed 또는 Europe PMC에서 수집됨
7. 요약 길이와 근거정보가 최소 기준을 충족함

기준 미충족 자료는 `data/auto_review_queue.json`에 저장되며 공개 대시보드에는 자동 반영되지 않습니다.

## 생성 파일

| 파일 | 용도 |
|---|---|
| `docs/data/auto_intelligence.json` | 검증된 공개 인텔리전스 원본 |
| `docs/data/knowledge_base.json` | 대시보드 정적 백업 및 카드 표시 데이터 |
| `docs/data/update_status.json` | 상태, 공개 건수, 검토대기 건수, 실패 소스 |
| `docs/data/index.json` | 기존 사업 인덱스에 자동 인텔리전스 병합 |
| `data/auto_review_queue.json` | 담당자 검토 대기 자료 |
| `data/auto_intelligence_state.json` | 중복 제거 및 공식페이지 변경 확인 상태 |

## 공개 대시보드 연결

`scripts/patch_frontend_v2.py`가 기존 `docs/index.html`의 Intelligence Hub를 한 번만 안전하게 패치합니다. 대시보드는 GitHub의 `knowledge_base.json`을 먼저 읽고, Apps Script Master DB가 응답하면 두 데이터를 URL·제목 기준으로 병합합니다. 따라서 Apps Script가 비어 있거나 일시적으로 실패해도 검증된 GitHub 자료가 계속 표시됩니다.

## 변경 최소화

- 동일 논문은 DOI → PMID → 정규화 제목 순서로 중복 제거합니다.
- 이미 수집한 자료의 최초 감지시각을 유지합니다.
- 의미 있는 데이터, 실패상태 또는 공식페이지 후보상태가 달라질 때만 JSON이 변경됩니다.
- GitHub Actions는 실제 파일 차이가 있을 때만 자동 커밋합니다.

## 운영 파일

- 엔진: `scripts/auto_intelligence_v2.py`
- 대시보드 연결 패치: `scripts/patch_frontend_v2.py`
- 소스 설정: `config/intelligence_sources_v2.json`
- 검증 완료 기본자료: `config/curated_intelligence.json`
- 단위시험: `tests/test_auto_intelligence_v2.py`, `tests/test_patch_frontend_v2.py`
- 자동실행: `.github/workflows/auto-intelligence.yml`

## 선택 설정

GitHub Repository Secrets에 `CROSSREF_MAILTO`를 추가하면 Crossref polite pool 요청에 사용할 수 있습니다. 키가 없어도 전체 구조는 작동합니다.

## 판단 원칙

자동 업데이트는 자료 탐색과 변경 감지를 담당합니다. 규제 적합성, 효능 표현, 최적 급여량, 제품 규격과 사업 의사결정은 공식 원문, 시험조건 및 전문가 검토 후 확정합니다.
