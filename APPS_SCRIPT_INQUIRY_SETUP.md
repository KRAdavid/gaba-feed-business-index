# GABA Feed 문의메일 직접수신 설정

## 변경 이유

기존 FormSubmit 진단 요청은 Cloudflare 보안 챌린지에서 HTTP 403으로 차단되었습니다. 따라서 외부 폼 중계서비스 대신 현재 운영 중인 Google Apps Script 웹 앱이 문의를 직접 받아 다음 작업을 수행하도록 전환합니다.

1. `dubaissday@cellpinda.com`으로 문의메일 발송
2. `dubaissday@gmail.com`으로 백업 메일 발송
3. 문의자의 이메일을 Reply-To로 지정
4. 문의자에게 접수 안내메일 발송
5. `GABA_Feed_Intelligence_Master_DB`의 `Inquiries` 시트에 모든 답변 기록

## 최초 1회 설치

1. [GABA_Feed_Intelligence_Master_DB](https://docs.google.com/spreadsheets/d/1QOYtwlq6uHp54BXu0v3yf5eA5B04HON9GxfxdE830zw/edit)를 엽니다.
2. 상단에서 **확장 프로그램 → Apps Script**를 선택합니다.
3. 왼쪽 `파일` 옆 **+**를 누르고 **스크립트**를 선택합니다.
4. 파일 이름을 `Inquiry`로 입력합니다.
5. 이 저장소의 `apps-script/Inquiry.gs` 전체 내용을 붙여넣고 저장합니다.
6. 우측 상단 **배포 → 배포 관리**를 엽니다.
7. 기존 웹 앱 배포의 연필 아이콘을 누릅니다.
8. 버전에서 **새 버전**을 선택한 뒤 배포합니다.
9. 권한 요청이 나오면 스프레드시트 편집과 이메일 발송 권한을 승인합니다.
10. 웹 앱 설정은 **실행 사용자: 나**, **액세스 권한: 모든 사용자**를 유지합니다.

기존 배포를 새 버전으로 갱신하면 `/exec` URL은 그대로 유지됩니다. 새 배포를 별도로 만들었다면 `docs/assets/inquiry-apps-script.js`의 `APPS_SCRIPT_URL`을 새 `/exec` 주소로 바꿔야 합니다.

## 정상 작동 확인

1. 공개 페이지를 `Ctrl + F5`로 새로고침합니다.
2. 주문 가이드 또는 사업협업 문의 폼에서 테스트 문의를 전송합니다.
3. 페이지에 `문의가 정상 접수되었습니다`와 문의번호가 표시되는지 확인합니다.
4. 다음 두 주소의 받은편지함과 스팸함을 확인합니다.
   - `dubaissday@cellpinda.com`
   - `dubaissday@gmail.com`
5. Master DB에 `Inquiries` 시트가 자동 생성되고 제출 내용이 한 행으로 기록되는지 확인합니다.

## 장애 확인

- 페이지에서 30초 이상 응답이 없으면 배포 관리에서 최신 버전이 적용됐는지 확인합니다.
- Apps Script 왼쪽의 **실행** 메뉴에서 `doPost` 오류 기록을 확인합니다.
- `MailApp daily quota exhausted`가 표시되면 Google 계정의 일일 발송 한도를 초과한 것입니다. 문의 내용은 `Inquiries` 시트에 기록되므로 담당자가 직접 회신할 수 있습니다.
- 웹 앱의 액세스 권한이 `나만`으로 되어 있으면 외부 사용자가 제출할 수 없습니다. 반드시 `모든 사용자`로 설정합니다.

## 개인정보 운영

문의정보는 사업협업 대응 목적으로만 사용합니다. 주민등록번호, 계좌번호, 건강정보, 비밀번호 또는 영업비밀 원문을 수집하지 않습니다. 보유기간과 파기절차는 회사 개인정보 처리방침에 맞춰 별도로 운영합니다.
