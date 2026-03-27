# OBS_GoogleDrive_QR

OBS 녹화 파일을 Google Drive에 업로드하고, 다운로드 QR 코드를 생성해 표시하는 PyQt6 애플리케이션입니다.

## Public 공개 전 보안 체크

- 관리자 비밀번호 하드코딩 제거 완료 (`settings.py`).
- 관리자 비밀번호는 아래 우선순위로 로드됩니다.
  1. 환경 변수 `BUT_ADMIN_PASSWORD`
  2. 앱 설정(`QSettings`)의 `admin_password`
- Google OAuth/토큰 파일이 저장소에 커밋되지 않도록 `.gitignore`를 강화했습니다.

## 실행

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

## 권장 운영 방식

1. 배포/운영 환경에서 `BUT_ADMIN_PASSWORD`를 반드시 설정하세요.
2. Google OAuth 자격 증명 JSON은 저장소 바깥에 두세요.
3. 공개 전에 Git 이력에서 민감정보 유출 이력이 없는지 점검하세요.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
