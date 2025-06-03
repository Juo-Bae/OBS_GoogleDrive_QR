import os
import sys
import pickle
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError, ResumableUploadError
from google.oauth2.credentials import Credentials

def resource_path(relative_path):
    """ PyInstaller 실행 파일 내 리소스 경로 반환 """
    try:
        base_path = sys._MEIPASS  # PyInstaller 환경
    except AttributeError:
        base_path = os.path.abspath(".")  # 개발 환경
    return os.path.join(base_path, relative_path)


class GoogleDriveUploader:
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self, settings):
        self.settings = settings
        self.connected = False
        self.credentials_path = resource_path(self.settings["google_api_file"])
        self.token_path = resource_path(f"{self.settings['google_api_folder_path']}/token.json")
        self.creds = None
        self.service = None
        if not self.connected and self.settings["google_api_file"] and self.settings['google_api_folder_path']:
            print(self.credentials_path)
            print(self.token_path)
            self._authenticate()
        else:
            print("❌ 구글 드라이브 인증 실패")
            self.connected = False
            

    def _authenticate(self):
        """인증 및 Drive API 서비스 객체 생성"""
        creds = None

        # 기존 토큰 존재 시 로드
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # 토큰이 없거나 만료된 경우
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"❌ 토큰 갱신 실패: {e}")
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    scopes=self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # 새 토큰 저장
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        self.creds = creds
        self.service = build('drive', 'v3', credentials=self.creds)
        self.connected = True
        print("✅ Google Drive 인증 완료")


    def upload_file(self, file_path, folder_id=None):
        try:
            file_name = os.path.basename(file_path)
            file_metadata = {'name': file_name}
            if folder_id:
                file_metadata['parents'] = [folder_id]

            # 🔁 매번 새로운 서비스 객체 생성
            creds = self.creds
            service = build('drive', 'v3', credentials=creds)

            with open(file_path, 'rb') as fh:
                media = MediaIoBaseUpload(fh, mimetype='video/mp4', resumable=True)

                request = service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                )

                response = None
                while response is None:
                    try:
                        status, response = request.next_chunk()
                        if status:
                            print(f"⏫ 업로드 진행률: {int(status.progress() * 100)}%")
                    except Exception as chunk_error:
                        print(f"❌ next_chunk 중 에러 발생: {chunk_error}")
                        return None

            if response and 'id' in response:
                file_id = response['id']
                print(f"✅ 업로드 완료: {file_name}, file_id: {file_id}")
                return f"https://drive.google.com/uc?export=download&id={file_id}"
            else:
                print("❌ 업로드 실패: 응답이 비어 있거나 ID 없음")
                return None

        except Exception as e:
            print(f"❌ 업로드 실패: {e}")
            return None