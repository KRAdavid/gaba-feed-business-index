# GABA Feed Business Model Index

사료업계가 처음인 사용자도 GABA 사료 사업의 **현재 준비도, 남은 핵심 검증, 최신 정책·연구·원료 시장 동향, 90일 실행계획**을 빠르게 파악할 수 있도록 만든 공개 인덱스입니다.

## 공개 화면

Production URL: [https://gaba-feed-business-index.dubaissday.chatgpt.site](https://gaba-feed-business-index.dubaissday.chatgpt.site)

현재 공개본은 감리를 마친 스냅샷입니다. Codex 주간 자동화가 매주 월요일 오전 9시 17분(한국 시간)에 공개 자료를 수집하고 검사한 뒤 사이트를 다시 배포합니다. `docs/`에는 사이트 원본이 있으며, `worker/`와 `scripts/build_site_worker.mjs`는 배포 파일을 만듭니다.

## 로컬 실행

```powershell
python scripts/update_public_index.py
python scripts/audit_korean_copy.py
python scripts/validate_public_index.py
python scripts/prepare_public_site.py
python -m http.server 8000 --directory docs
```

브라우저에서 `http://localhost:8000`을 엽니다. `index.html`을 파일로 직접 열면 브라우저 보안 정책 때문에 JSON을 불러올 수 없습니다.

## GitHub Pages 미러링(선택)

별도 GitHub Pages 미러가 필요하면 빈 공개 저장소를 만든 뒤 아래 명령으로 검증·커밋·push할 수 있습니다.

```powershell
.\scripts\publish_github_pages.ps1 `
  -RepositoryUrl "https://github.com/OWNER/REPOSITORY.git" `
  -Branch main `
  -AuthorName "YOUR NAME" `
  -AuthorEmail "YOUR EMAIL"
```

push가 끝나면 저장소의 **Settings → Pages → Source**를 `GitHub Actions`로 선택하고 `Refresh and publish public index` 워크플로를 한 번 실행합니다.

## 자동 업데이트

- 매주 월요일 오전 9시 17분(한국 시간)에 농림축산식품부 RSS, Europe PMC, 세계은행 원료 가격 자료를 확인하고 공개 사이트를 갱신합니다.
- 자료를 새로 받지 못하면 이전 스냅샷을 유지하고 화면에 `이전 자료 사용`이라고 표시합니다.
- 자동 수집된 신호는 `검토 대기`로 표시되며 준비도 점수에 자동 반영되지 않습니다.
- 담당자가 원문, 대상 축종, 용량, 시험 설계, 통계 결과를 검토한 뒤 `data/manual_signals.json`과 `data/base_index.json`을 갱신해야 점수가 바뀝니다.
- 갱신 결과와 변경 이력은 Git 커밋으로 남습니다.

## 데이터 구조

- `data/base_index.json` — 검토 완료된 준비도·검증 항목·가정·로드맵·용어·출처
- `data/manual_signals.json` — 담당자가 검토한 정책·연구·내부모델 신호
- `docs/data/index.json` — 공개 사이트가 읽는 최신 스냅샷
- `scripts/update_public_index.py` — 공개 원천 수집 및 스냅샷 생성
- `scripts/validate_public_index.py` — 점수·필수 필드·출처 링크 불변조건 검증
- `scripts/audit_korean_copy.py` — 어색한 번역투와 금지 표현을 찾는 한국어 문장 감리
- `KOREAN_COPY_AUDIT.md` — 감리 범위와 최종 검사 결과 기록
- `tests/` — 파서와 오프라인 복구 테스트
- `.openai/hosting.json` — 기존 Sites 프로젝트를 재사용하기 위한 호스팅 식별자
- `worker/` — 공개 사이트를 제공하는 Sites Worker 원본

## 운영 원칙

이 인덱스는 투자·법률·수의학 분야의 확정 의견이 아닙니다. 규제 분류, 표시 가능 문구, 축종별 유효 용량, OEM 조건, 고객의 구매 의사는 각각 서면 자료로 확인합니다. 공개 전에는 한국어 문장 감리를 거치며, 모든 자료의 마지막 공개 섹션은 `APPENDIX · 부록`으로 유지합니다.
