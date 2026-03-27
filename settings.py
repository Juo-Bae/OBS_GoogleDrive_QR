from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QRadioButton, QSpinBox, QPushButton, 
                             QButtonGroup, QFormLayout, QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
import os
import hmac


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("비밀번호 확인")
        self.setFixedWidth(300)
        
        layout = QVBoxLayout()
        
        # 비밀번호 입력 필드
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("비밀번호를 입력하세요")
        
        # 버튼 레이아웃
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("확인")
        self.cancel_button = QPushButton("취소")
        
        self.ok_button.clicked.connect(self.verify_password)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # 레이아웃에 위젯 추가
        layout.addWidget(QLabel("설정을 변경하려면 비밀번호를 입력하세요:"))
        layout.addWidget(self.password_input)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
    def verify_password(self):
        expected_password = self._load_expected_password()
        if not expected_password:
            QMessageBox.critical(
                self,
                "보안 설정 필요",
                "관리자 비밀번호가 설정되지 않았습니다.\n"
                "환경 변수 BUT_ADMIN_PASSWORD 또는 설정의 관리자 비밀번호를 지정해주세요."
            )
            return

        if hmac.compare_digest(self.password_input.text(), expected_password):
            self.accept()
        else:
            QMessageBox.warning(self, "오류", "비밀번호가 일치하지 않습니다.")
            self.password_input.clear()

    @staticmethod
    def _load_expected_password():
        env_password = os.getenv("BUT_ADMIN_PASSWORD", "").strip()
        if env_password:
            return env_password

        settings = QSettings("BUT", "config")
        return settings.value("admin_password", "").strip()

class SettingsDialog(QDialog):
    # 설정 변경 시그널 추가
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("설정")
        self.setMinimumWidth(400)
            
        # 메인 레이아웃
        layout = QVBoxLayout()

        # 1. 모니터 방향 설정
        direction_group = QButtonGroup(self)
        direction_layout = QHBoxLayout()
        
        self.landscape_radio = QRadioButton("가로")
        self.portrait_radio = QRadioButton("세로")
        self.landscape_radio.setChecked(True)  # 기본값은 가로
        
        direction_group.addButton(self.landscape_radio)
        direction_group.addButton(self.portrait_radio)
        
        direction_layout.addWidget(QLabel("모니터 방향:"))
        direction_layout.addWidget(self.landscape_radio)
        direction_layout.addWidget(self.portrait_radio)
        direction_layout.addStretch()

        form_layout = QFormLayout()  # 🔹 먼저 선언 필요

        # OBS 서버 비밀번호
        self.obs_password = QLineEdit()
        form_layout.addRow("OBS 서버 비밀번호", self.obs_password)

        # 2. 구글 API 인증 파일 경로
        # 🔹 QLineEdit 필드
        self.google_api_path = QLineEdit()
        self.google_api_path.setPlaceholderText("클라이언트 secret JSON 파일 경로")

        # 🔹 파일 선택 버튼
        select_button = QPushButton("찾아보기")
        select_button.clicked.connect(self.select_api_file)

        form_layout.addRow("Google API 인증 파일:", self.google_api_path)
        form_layout.addWidget(select_button)

        # 3. 구글 드라이브 폴더 ID
        self.google_folder_id = QLineEdit()
        self.google_folder_id.setPlaceholderText("예: 1AbCdEfGhIjKlMnOpQRsTuvWxYz")
        form_layout.addRow("구글 드라이브 폴더 ID:", self.google_folder_id)
        
        # 4. 새로고침 시간
        self.refresh_time = QSpinBox()
        self.refresh_time.setRange(1, 60)
        self.refresh_time.setValue(30)  # 기본값 30초
        self.refresh_time.setSuffix(" 초")
        
        # 5. 최대 동영상 촬영 시간
        self.max_video_time = QSpinBox()
        self.max_video_time.setRange(1, 120)
        self.max_video_time.setValue(60)  # 기본값 60초
        self.max_video_time.setSuffix(" 초")

        # 6. 창 높이 설정
        self.window_height = QSpinBox()
        self.window_height.setRange(100, 1080)
        self.window_height.setValue(380)  # 기본값 380
        self.window_height.setSuffix(" px")

        # 7. 관리자 비밀번호
        self.admin_password = QLineEdit()
        self.admin_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.admin_password.setPlaceholderText("환경 변수 BUT_ADMIN_PASSWORD 사용 권장")
        
        form_layout.addRow("새로고침 시간:", self.refresh_time)
        form_layout.addRow("최대 동영상 촬영 시간:", self.max_video_time)
        form_layout.addRow("창 높이:", self.window_height)
        form_layout.addRow("관리자 비밀번호:", self.admin_password)

        # 설정 변경 시 시그널 연결
        self.landscape_radio.toggled.connect(self.update_preview)
        self.portrait_radio.toggled.connect(self.update_preview)
        self.window_height.valueChanged.connect(self.update_preview)
        
        # 확인/취소/미리보기 버튼
        button_layout = QHBoxLayout()
        self.reset_button = QPushButton("초기화")
        self.ok_button = QPushButton("확인")
        self.cancel_button = QPushButton("취소")
        
        self.reset_button.clicked.connect(self.reset_settings)
        self.ok_button.clicked.connect(self.handle_accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.reset_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # 모든 레이아웃 추가
        layout.addLayout(form_layout)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)

        # 설정 로드
        self.load_settings()


    def reset_settings(self):
        """설정값 초기화 및 기본값으로 저장"""
        print("reset_settings")
        settings = QSettings("BUT", "config")
        settings.clear()

        # 기본값 설정
        default_values = {
            "obs_password": "",
            "orientation": "landscape",
            "google_folder_id": "",
            "refresh_time": 30,
            "max_video_time": 60,
            "window_height": 380,
            "google_api_file": "",
            "admin_password": ""
        }

        # 설정값 저장
        for key, value in default_values.items():
            settings.setValue(key, value)

        settings.sync()  # 설정 강제 저장
        self.load_settings()


    def update_preview(self):
        """설정값 미리보기 업데이트"""
        settings = self.get_settings()
        self.settings_changed.emit(settings)
    
    def handle_accept(self):
        self.save_settings()
        if self.parent:
            self.parent.nextStep()
        self.accept()        
    
    def save_settings(self):
        settings = QSettings("BUT", "config")
        config = self.get_settings()
        for key, value in config.items():
            settings.setValue(key, value)

    def load_settings(self):
        settings = QSettings("BUT", "config")

        # OBS 비밀번호
        self.obs_password.setText(settings.value("obs_password", ""))

        # 방향 설정
        orientation = settings.value("orientation", "landscape")
        self.landscape_radio.setChecked(orientation == "landscape")
        self.portrait_radio.setChecked(orientation == "portrait")

        # 값 복원
        self.google_folder_id.clear()
        self.google_folder_id.setText(settings.value("google_folder_id", ""))

        self.refresh_time.setValue(int(settings.value("refresh_time", 30)))
        self.max_video_time.setValue(int(settings.value("max_video_time", 60)))
        self.window_height.setValue(int(settings.value("window_height", 380)))

        # Google API 경로 복원
        self.google_api_path.clear()
        self.google_api_path.setText(settings.value("google_api_file", ""))
        self.admin_password.setText(settings.value("admin_password", ""))



    def get_settings(self):
        """설정값을 딕셔너리로 반환"""
        google_api_file = self.google_api_path.text()
        return {
            "obs_password": self.obs_password.text(),
            'orientation': 'landscape' if self.landscape_radio.isChecked() else 'portrait',
            'google_folder_id': self.google_folder_id.text(),
            'refresh_time': self.refresh_time.value(),
            'max_video_time': self.max_video_time.value(),
            'window_height': self.window_height.value(),
            'google_api_file': google_api_file,
            'google_api_folder_path': os.path.dirname(google_api_file),
            'admin_password': self.admin_password.text()
        }

    
    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "폴더 선택")
        if folder:
            self.save_folder_input.setText(folder)
            self.update_preview()

    # 🔹 파일 선택 함수
    def select_api_file(self):
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        file_dialog.setNameFilter("JSON Files (*.json)")
        if file_dialog.exec():
            selected_file = file_dialog.selectedFiles()[0]
            self.google_api_path.setText(selected_file)
