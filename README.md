# OBS Google Drive QR

PyQt6 기반의 데스크톱 앱으로,

1. OBS 녹화를 시작/종료하고,
2. 녹화 파일을 Google Drive에 업로드한 뒤,
3. 다운로드 링크 QR 코드를 화면에 표시합니다.

---

## 주요 기능

- OBS WebSocket(기본 `localhost:4455`) 연동
- 녹화 종료 후 Google Drive 업로드
- 업로드된 파일의 다운로드 링크를 QR 코드로 생성/표시
- 설정 UI 제공 (OBS 비밀번호, Google API JSON 경로, 폴더 ID, 타이머 등)
- 관리자 비밀번호 보호 (`BUT_ADMIN_PASSWORD` 또는 앱 설정값)

---

## 요구 사항

- Python 3.10+
- OBS Studio + WebSocket 활성화
- Google Cloud OAuth Client JSON 파일

---

## 설치

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 추가 의존성 (현재 requirements.txt에 없는 항목)
pip install obsws-python qrcode pynput google-api-python-client google-auth-oauthlib google-auth
```

---

## 실행

```bash
python main.py
```

---

## 설정 방법

앱 실행 후 설정(⚙️)에서 아래 값을 입력합니다.

- **OBS 서버 비밀번호**: OBS WebSocket 비밀번호
- **Google API 인증 파일**: OAuth client JSON 파일 경로
- **구글 드라이브 폴더 ID**: 업로드 대상 Drive 폴더 ID
- **새로고침 시간 / 최대 녹화 시간 / 창 높이**
- **관리자 비밀번호**: 설정 접근용 비밀번호 (권장: 환경변수 사용)

### 관리자 비밀번호 우선순위

1. 환경 변수 `BUT_ADMIN_PASSWORD`
2. 앱 로컬 설정(`QSettings`)의 `admin_password`

운영 환경에서는 환경 변수 사용을 권장합니다.

예시:

```bash
export BUT_ADMIN_PASSWORD='change-this-password'
python main.py
```

---

## 공개(Public) 전 보안 체크리스트

- [ ] `BUT_ADMIN_PASSWORD` 설정 완료
- [ ] OAuth JSON / token 파일이 Git에 커밋되지 않았는지 확인
- [ ] 필요 시 Git 히스토리 민감정보 스캔 수행
- [ ] Google Drive 폴더 권한 최소화(필요한 계정만 접근)

`.gitignore`에는 아래 민감 파일 패턴이 포함되어 있습니다.

- `*.googleusercontent.*.json`
- `client_secret*.json`
- `credentials*.json`
- `secrets*.json`
- `token.json`
- `token.pickle`

---

## 프로젝트 구조

- `main.py` - 메인 UI/녹화 흐름 제어
- `settings.py` - 설정 UI 및 비밀번호 검증
- `obsController.py` - OBS WebSocket 제어
- `googleController.py` - Google Drive 인증/업로드
- `QRController.py` - QR 생성/표시
- `usage.py` - 사용법 다이얼로그

---

## 트러블슈팅

### 1) OBS 연결 실패

- OBS WebSocket 활성화 여부 확인
- 포트(기본 4455), 비밀번호 일치 여부 확인

### 2) Google 인증 실패

- OAuth client JSON 경로가 올바른지 확인
- 브라우저 인증 절차 완료 여부 확인
- 토큰 파일 권한 확인

### 3) 업로드는 되는데 다운로드가 안 됨

- 업로드된 파일의 Drive 공유 권한 확인
- 사용 중인 링크 정책(조직/외부 공유 제한) 확인

---

## 라이선스

MIT License. 자세한 내용은 [LICENSE](LICENSE) 파일을 참고하세요.
