# GABA 공개 사이트 배포 안내

이 폴더는 별도 빌드나 서버 프로그램이 필요 없는 정적 배포본입니다. `index.html`이 현재 폴더의 최상위에 있어야 합니다.

## 가장 빠른 배포

1. `GABA_Feed_Public_Site_Static_Deploy.zip`을 정적 웹호스팅의 직접 업로드 화면에 올립니다.
2. 업로드가 끝나면 발급된 공개 주소에서 첫 화면을 엽니다.
3. `data/index.json`, `health.json`, 다운로드 자료 3종이 열리는지 확인합니다.
4. 데스크톱과 모바일에서 가로 넘침과 콘솔 오류가 없는지 확인합니다.

Cloudflare Pages의 Direct Upload는 미리 만든 정적 폴더나 ZIP 업로드를 지원합니다.
https://developers.cloudflare.com/pages/get-started/direct-upload/

Cloudflare Pages 프로젝트와 `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID` 환경변수가 준비되어 있다면 저장소 루트에서 다음 명령으로 검증과 배포를 함께 실행할 수 있습니다.

```powershell
.\scripts\publish_cloudflare_pages.ps1 -ProjectName gaba-feed-business-index
```

GitHub Pages 자동 배포를 사용할 때는 저장소 루트의 `.github/workflows/public-index.yml`을 사용합니다.
https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

## 업데이트 후 새 배포본 만들기

저장소 루트에서 다음 명령을 실행합니다.

```powershell
python scripts/update_public_index.py
python scripts/localize_portable_artifact.py
python scripts/audit_korean_copy.py
python scripts/validate_public_index.py
python scripts/prepare_public_site.py
python scripts/validate_public_site.py
python scripts/build_static_release.py
python scripts/validate_static_release.py
```

검증 오류가 하나라도 있으면 배포하지 않습니다. 새 ZIP을 올릴 때는 기존 정상 배포를 삭제하기 전에 새 버전의 화면과 다운로드를 먼저 확인합니다.

## 배포 후 확인 주소

- `/` — 공개 인덱스
- `/data/index.json` — 최신 데이터 스냅샷
- `/health.json` — 배포본 상태와 버전
- `/downloads/GABA_Index_Master.xlsx` — 관리 원장
- `/downloads/GABA_Feed_Business_Model_Speech_Deck_v1.pptx` — 스피치덱
- `/downloads/GABA_Index_운영가이드.md` — 운영 가이드

## 도메인을 확정한 뒤

이 배포본은 어느 도메인에서도 사용할 수 있도록 특정 공개 주소를 고정하지 않았습니다. 최종 도메인이 확정되면 원본 `docs/index.html`의 `canonical`과 `og:url`을 실제 주소로 바꾼 뒤 패키지를 다시 만듭니다.
