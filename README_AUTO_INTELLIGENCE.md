# GABA Feed Auto Intelligence v1

## 구현 범위

- PubMed 자동 수집
- Europe PMC 자동 수집
- Crossref 자동 수집
- DOI·PMID·제목 기반 중복 제거
- 축종 자동 분류
- 근거수준 A~D 자동 분류
- 공식 정책·시장·통계 페이지 변경 감지
- 자동 공개와 검토 대기 자동 분리
- 기존 `docs/data/index.json`에 `auto_intelligence` 항목 병합
- 매일 03:20(KST) GitHub Actions 자동 실행
- 데이터 변경 시 자동 커밋
- Cloudflare Pages 자동 재배포

## 자동 공개 원칙

논문:
- DOI 또는 PMID 존재
- PubMed·Europe PMC·Crossref 출처
- 최소 요약 길이 충족
- GABA와 동물영양 관련성 동시 충족

정책·통계·시장:
- 공식기관 URL만 자동 공개
- 페이지 변경 감지는 변경 사실만 알리며 법적 해석을 자동 확정하지 않음

기준 미충족 자료는 `data/auto_review_queue.json`에 저장되지만 웹에는 공개되지 않습니다.

## 저장소 반영

이 패키지의 폴더를 저장소 루트에 병합합니다.

- `scripts/auto_intelligence.py`
- `config/intelligence_sources.json`
- `.github/workflows/auto-intelligence.yml`
- `tests/test_auto_intelligence.py`

기존 파일은 삭제하지 않습니다.

## 최초 확인

GitHub → Actions → `Auto-update GABA feed intelligence` → Run workflow

정상 실행 후 생성되는 파일:

- `docs/data/auto_intelligence.json`
- `data/auto_review_queue.json`
- `data/auto_intelligence_state.json`

기존 `docs/data/index.json`에는 `auto_intelligence` 키가 추가됩니다.

## 선택적 무료 API 키

키가 없어도 논문 수집과 공식 페이지 변경 감지는 작동합니다.

선택적으로 GitHub Secrets에 추가할 수 있습니다.

- `CROSSREF_MAILTO`: Crossref polite pool용 이메일
- `KOSIS_API_KEY`: KOSIS 통계 API
- `USDA_NASS_API_KEY`: USDA NASS QuickStats API

KOSIS·USDA 수치형 데이터 어댑터는 다음 버전에서 소스별 통계표 ID가 확정된 후 활성화합니다.

## 한계

- 초록이 없는 논문은 낮은 근거등급 또는 검토 대기로 분류될 수 있음
- 공식 페이지 변경 감지는 구조 변경도 감지할 수 있음
- 자동 요약은 초록 기반 추출식 요약이며 생성형 AI의 해석이 아님
- 규제와 효능 판단은 공식 원문 및 전문가 검토가 필요
