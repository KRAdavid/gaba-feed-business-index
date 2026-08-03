# GABA Feed Business Model Index

사료업계 경험이 없는 사용자도 GABA 사료 사업의 **현재 준비도, 열린 검증 게이트, 최신 정책·연구·원료시장 신호, 다음 90일 행동**을 빠르게 판단할 수 있도록 만든 공개 운영 인덱스입니다.

## 공개 화면

`docs/`가 GitHub Pages 배포 루트입니다. 저장소를 GitHub에 연결하고 **Settings → Pages → Source: GitHub Actions**를 선택하면 `.github/workflows/public-index.yml`이 사이트를 배포합니다.

## 로컬 실행

```powershell
python scripts/update_public_index.py
python scripts/validate_public_index.py
python scripts/prepare_public_site.py
python -m http.server 8000 --directory docs
```

브라우저에서 `http://localhost:8000`을 엽니다. `index.html`을 파일로 직접 열면 브라우저 보안 정책 때문에 JSON을 불러올 수 없습니다.

## 최초 공개

빈 공개 GitHub 저장소를 만든 뒤 아래 명령 하나로 검증·커밋·push까지 수행할 수 있습니다.

```powershell
.\scripts\publish_github_pages.ps1 `
  -RepositoryUrl "https://github.com/OWNER/REPOSITORY.git" `
  -Branch main `
  -AuthorName "YOUR NAME" `
  -AuthorEmail "YOUR EMAIL"
```

push가 끝나면 저장소의 **Settings → Pages → Source**를 `GitHub Actions`로 선택하고 `Refresh and publish public index` 워크플로를 한 번 실행합니다. 이후에는 예약 갱신과 배포가 자동으로 이어집니다.

## 자동 업데이트

- 매주 월요일 09:17 KST에 농림축산식품부 RSS, Europe PMC, World Bank Pink Sheet 원료가격 데이터를 확인합니다.
- 원천 연결이 실패하면 이전 스냅샷을 유지하고 화면에 `이전값` 상태를 표시합니다.
- 자동 수집된 신호는 `검토 대기`로 표시되며 준비도 점수에 자동 반영되지 않습니다.
- 담당자가 원문·대상 축종·용량·시험설계·통계 결과를 검토한 뒤 `data/manual_signals.json`과 `data/base_index.json`을 갱신해야 점수가 바뀝니다.
- 갱신 결과와 변경 이력은 Git 커밋으로 남습니다.

## 데이터 구조

- `data/base_index.json` — 검토 완료된 준비도·게이트·가정·로드맵·용어·출처
- `data/manual_signals.json` — 담당자가 검토한 정책·연구·내부모델 신호
- `docs/data/index.json` — 공개 사이트가 읽는 최신 스냅샷
- `scripts/update_public_index.py` — 공개 원천 수집 및 스냅샷 생성
- `scripts/validate_public_index.py` — 점수·필수 필드·출처 링크 불변조건 검증
- `tests/` — 파서와 오프라인 복구 테스트

## 운영 원칙

이 인덱스는 투자·법률·수의학적 확정 의견이 아닙니다. 규제 분류, 표시 가능 문구, 축종별 유효 용량, OEM 조건, 고객 지불의사는 각각 서면 근거로 검증합니다. 모든 자료의 마지막 공개 섹션은 `Appendix`이며 용어 주석, 공개 원천, 이용 한계를 포함합니다.
