import sys, os, time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QRect, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

from settings import SettingsDialog, PasswordDialog
from usage import UsageDialog

import json
import threading
import time
from pynput import mouse, keyboard


from obsController import OBSController
from googleController import GoogleDriveUploader
from QRController import generate_qr, QRDialog


class ClickSignalHandler(QObject):
    key_pressed = pyqtSignal(str)  # 키 이름을 문자열로 전달

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BUT")

        self.dialog = SettingsDialog(self)
        self.usage_dialog = None
        self.qr_dialog = None
        self.settings = self.dialog.get_settings()

        self.obs_controller = None
        self.file_name = None
        self.url = None
        self.google_uploader = None
        self.first_open_setting = False


        # 키 입력 신호 핸들러 초기화
        self.click_signal_handler = ClickSignalHandler()
        self.click_signal_handler.key_pressed.connect(self.handle_key_event)
        self.start_key_listener()

        self.show_settings()


    def nextStep(self):
        if self.first_open_setting == False:
            self.first_open_setting = True
            self.obsInit()

    def obsInit(self):
        self.obs_controller = OBSController(password=self.settings['obs_password'])
        config_path = os.path.join(self.obs_controller.record_directory, "config")
        os.makedirs(config_path, exist_ok=True)
        self.setWindow()

    def setWindow(self):
        # 프레임리스 윈도우와 항상 위 고정 플래그 설정
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        
        # 화면 크기 가져오기
        screen = QApplication.primaryScreen().geometry()
        self.window_height = 380  # 기본 높이

        # 창 크기 설정 (화면 너비에 맞추고 하단에 위치)
        self.setGeometry(0, screen.height() - self.window_height, 
                        screen.width(), self.window_height)



        # 중앙 위젯 생성
        central_widget = QWidget()
        central_widget.setStyleSheet("""
            background-color: #EBD4BC;
            border: 5px solid #E795B9;
            border-radius: 10px;
        """)
        self.setCentralWidget(central_widget)

        # 메인 레이아웃
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 0)  # 여백 설정
        central_widget.setLayout(main_layout)


        # 오류 레이블
        self.error_label = QLabel("")
        self.error_label.setFont(QFont("Arial", 20))
        self.error_label.setStyleSheet("""
            QLabel {
                border: none;
                color: red;
                background-color: transparent;
            }
        """)
        
        # 툴바 컨테이너 생성
        toolbar_container = QWidget()
        toolbar_container.setMinimumHeight(65)  # 최소 높이 설정
        toolbar_container.setStyleSheet("""
            QWidget {
                background-color: none;
                border: none;
            }
        """)

        # 툴바 레이아웃
        toolbar_layout = QHBoxLayout(toolbar_container)
        toolbar_layout.setContentsMargins(20, 10, 20, 10)

        # 설정 버튼
        settings_button = QPushButton("⚙️")
        settings_button.setFixedSize(30, 30)
        settings_button.setFont(QFont("Arial", 16))
        settings_button.clicked.connect(self.show_settings)
        settings_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 15px;
            }
        """)

        # 사용법 버튼
        usage_button = QPushButton("💡")
        usage_button.setFixedSize(30, 30)
        usage_button.setFont(QFont("Arial", 16))
        usage_button.clicked.connect(self.show_usage)
        usage_button.setStyleSheet("""
            QPushButton {
                border: none;
                background: transparent;
            }
            QPushButton:hover {
                background: rgba(0, 0, 0, 0.1);
                border-radius: 15px;
            }
        """)

        # On Air 레이블
        self.on_air_label = QLabel("")
        self.on_air_label.setFont(QFont("Arial", 16))
        self.on_air_label.setStyleSheet("border: none;")

        # 좌우 배치
        toolbar_layout.addWidget(self.on_air_label)
        toolbar_layout.addStretch()
        toolbar_layout.addWidget(usage_button)
        toolbar_layout.addWidget(settings_button)

        # 메인 레이아웃에 추가
        main_layout.addWidget(toolbar_container)

        
        # 촬영 컨트롤 레이아웃
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(20, 20, 20, 0)  # 상단 여백 추가
        

        self.timer_label = QLabel(f"")
        self.timer_label.setFont(QFont("Arial", 64, QFont.Weight.Bold))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.timer_label.setStyleSheet("""
            QLabel {
                color: #333;
                background: #FFFFFF;
                border: none;
                border-radius: 20px;
                padding: 20px;
                min-width: 200px;
            }
        """)
        
        # 촬영 버튼
        self.record_button = QPushButton("⏺")
        self.record_button.setFixedSize(80, 80)
        self.record_button.setFont(QFont("Arial", 32))
        self.record_button.setCheckable(True)
        self.record_button.clicked.connect(self.toggle_recording)
        self.is_recording = False
        self.update_record_button_style()


        # 리모컨 설명 레이아웃
        remote_control_layout = QHBoxLayout()
        label_2 = QLabel(" 🔴 녹화 시작/중지 \t🔵 사용법 보기")
        label_2.setAlignment(Qt.AlignmentFlag.AlignRight)
        label_2.setFont(QFont("Arial", 24))
        label_2.setStyleSheet("""
            border: none;
            color: #333;
        """)
        remote_control_layout.addWidget(label_2)
        
        # 🔻 연결 실패 시 버튼 비활성화
        if not self.obs_controller.connected:
            self.record_button.setEnabled(False)
            self.error_label.setText("❌ OBS 연결에 실패했습니다.")

        # 구글 드라이브 업로드 컨트롤러 초기화
        self.init_google()
        
        # 레이아웃에 위젯 추가
        control_layout.addWidget(self.timer_label)
        # control_layout.addWidget(self.record_button)
        main_layout.addLayout(toolbar_layout)
        main_layout.addLayout(control_layout)
        main_layout.addStretch()  # 하단 여백을 위한 스트레치
        main_layout.addLayout(remote_control_layout)
        main_layout.addWidget(self.error_label)

    def update_record_button_style(self):
        obs_ok = self.obs_controller.connected
        gdrive_ok = self.google_uploader is not None
        current_settings = self.dialog.get_settings()
        folder_ok = bool(current_settings["google_folder_id"].strip())

        if obs_ok and gdrive_ok and folder_ok:
            self.record_button.setText("⏺")  # 예: 정지 버튼으로 바꾸기
            self.record_button.setEnabled(True)
            self.record_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: #ff4444;
                    border-radius: 40px;
                    color: white;
                }
                QPushButton:hover {
                    background: #ff6666;
                }
                QPushButton:checked {
                    background: #444;
                }
            """)
        else:
            self.record_button.setText("⏹")
            self.record_button.setEnabled(False)
            self.record_button.setStyleSheet("""
                QPushButton {
                    border: none;
                    background: #444;
                    color: #aaa;
                    border-radius: 5px;
                }
            """)

    def toggle_recording(self):
        if not self.obs_controller.connected:
            QMessageBox.warning(self, "오류", "OBS 연결에 실패했습니다.")
            self.error_label.setText("❌ OBS 연결에 실패했습니다.")
            return

        if self.google_uploader == None:
            QMessageBox.warning(self, "오류", "구글 드라이브 연결에 실패했습니다.")
            self.error_label.setText("❌ 구글 드라이브 연결에 실패했습니다.")
            return

        current_settings = self.dialog.get_settings()  # 최신값으로 다시 가져옴
        if not current_settings["google_folder_id"].strip():
            QMessageBox.warning(self, "오류", "Google Drive 폴더 ID가 설정되어 있지 않습니다.")
            self.error_label.setText("❌ Google Drive 폴더 ID가 비어 있습니다.")
            return

        if not self.is_recording:
            
            # OBS 녹화 시작
            if self.obs_controller.start_recording():

                # 초기 설정값 가져오기
                initial_time = int(self.settings['max_video_time'])
                minutes = initial_time // 60
                seconds = initial_time % 60
                
                # 타이머 레이블
                self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

                # 타이머 설정
                self.timer = QTimer()
                self.timer.timeout.connect(self.update_timer)
                self.remaining_time = initial_time

                # 녹화중 레이블
                self.on_air_label.setText("녹화중")
                self.on_air_label.setStyleSheet("""
                    QLabel {
                        color: white;
                        background: #cc0000;
                        border-radius: 10px;
                        padding: 10px;
                    }
                """)

                # 촬영 시작
                self.is_recording = True
                self.record_button.setChecked(True)
                self.timer.start(1000)  # 1초마다 업데이트
            else:
                QMessageBox.warning(self, "오류", "OBS 녹화를 시작할 수 없습니다.")
        else:
            # 저장중 레이블
            self.timer.stop()
            self.on_air_label.setText("저장중")
            self.on_air_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background: #0000cc;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            self.timer_label.setText(f"저장중")
            # 3초 뒤에 stop + QR + 라벨 초기화 실행
            QTimer.singleShot(1000, self._finish_after_saving)
            
        self.update_record_button_style()

    def stop_recording(self):
        try:
            # OBS 녹화 중지
            self.obs_controller.stop_recording()
            
            self.is_recording = False
            self.record_button.setChecked(False)

            # 타이머 레이블 초기화
            self.timer_label.setText(f"")
        
            QTimer.singleShot(1000, self.upload_latest_recording)

        except Exception as e:
            print(f"❌ 녹화 중지 실패: {e}")

    def upload_latest_recording(self):
        """가장 최근 녹화 파일을 업로드하는 함수"""
        def get_latest_file(folder_path: str) -> str:
            try:
                files = [os.path.join(folder_path, f) for f in os.listdir(folder_path)]
                files = [f for f in files if os.path.isfile(f)]
                
                if not files:
                    return None
                return max(files, key=os.path.getmtime)
            except Exception as e:
                print(f"❌ 최근 파일 경로 가져오기 실패: {e}")
                return None

        latest_file = get_latest_file(self.obs_controller.record_directory)
        if latest_file:
            self.file_name = os.path.basename(latest_file).split(".")[0]
            self.url = self.google_uploader.upload_file(
                latest_file,
                folder_id=self.settings["google_folder_id"]
            )
            print(f"✅ 업로드 완료: {self.file_name} ({self.url})")
            # ✅ 업로드 완료 후 QR 출력
            QTimer.singleShot(1000, self.show_qr_dialog)
        else:
            print("❌ 업로드할 파일이 없습니다.")

    def update_timer(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_timer_display()
        else:
            # 저장중 레이블
            self.timer.stop()
            self.on_air_label.setText("저장중")
            self.on_air_label.setStyleSheet("""
                QLabel {
                    color: white;
                    background: #0000cc;
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            self.timer_label.setText(f"저장중")
            # 3초 뒤에 stop + QR + 라벨 초기화 실행
            QTimer.singleShot(1000, self._finish_after_saving)

    def update_timer_display(self):
        minutes = self.remaining_time // 60
        seconds = self.remaining_time % 60
        self.timer_label.setText(f"{minutes:02d}:{seconds:02d}")

    def show_qr_dialog(self):
        self.on_air_label.setText("")
        self.on_air_label.setStyleSheet("QLabel { border: none; }")
        self.timer_label.setText("")

        if self.url:
            # QR 이미지 생성 및 표시
            qr_path = generate_qr(self.file_name, self.url, self.obs_controller.record_directory)
            print(f"✅ QR 이미지 경로: {qr_path}")

            # 이미 불러온 설정값에서 새로고침 시간 사용
            refresh_seconds = int(self.settings['refresh_time'])

            # QR 표시 다이얼로그 띄우기
            self.qr_dialog = QRDialog(qr_path, timeout_seconds=refresh_seconds, parent=self)
            self.qr_dialog.closed.connect(self.on_qr_dialog_closed)
            self.qr_dialog.show()
            self.url = None
        else:
            # 촬영 종료 팝업 표시
            QMessageBox.information(self, "ERROR", "QR 출력 실패")
            self.qr_dialog.close()

    def close_qr_dialog(self):
        if self.qr_dialog:
            self.qr_dialog.close()  # 반드시 close()로!
            self.qr_dialog = None
            # QTimer.singleShot(1000, self.show_usage)
        

    def on_qr_dialog_closed(self):
        print("메인: QR 다이얼로그 닫힘 처리")
        self.qr_dialog = None
        QTimer.singleShot(1000, self.show_usage)

    def show_settings(self):
        # 비밀번호 확인 다이얼로그 표시
        password_dialog = PasswordDialog(self)
        if password_dialog.exec() == PasswordDialog.DialogCode.Accepted:
            # 미리보기 시그널 연결
            self.dialog.settings_changed.connect(self.preview_settings)
            
            if self.dialog.exec() == SettingsDialog.DialogCode.Accepted:
                # 확인 버튼을 눌렀을 때만 설정 적용
                self.apply_settings(self.dialog.get_settings())
                
            else:
                # 취소 버튼을 눌렀을 때 이전 설정으로 복원
                self.restore_previous_settings()

    def show_usage(self):
        if self.usage_dialog and self.usage_dialog.isVisible():
            self.usage_dialog.close()
            self.usage_dialog = None
        else:
            self.usage_dialog = UsageDialog(self)
            self.usage_dialog.show()

    def preview_settings(self, settings):
        """설정 미리보기"""
        # 창 높이 업데이트
        self.window_height = settings['window_height']
        screen = QApplication.primaryScreen().geometry()
        
        # 창 크기 설정 (화면 너비에 맞추고 하단에 위치)
        self.setGeometry(0, screen.height() - self.window_height, 
                        screen.width(), self.window_height)

    def apply_settings(self, settings):
        """설정 적용"""
        self.preview_settings(settings)
        # 타이머 값도 업데이트
        self.remaining_time = int(settings['max_video_time'])

    def restore_previous_settings(self):
        """이전 설정으로 복원"""
        pass

    def closeEvent(self, event):
        """프로그램 종료 시 OBS 연결 해제"""
        self.obs_controller.close()
        event.accept()

    def init_google(self):
        try:
            print("init_google")
            if not self.obs_controller.connected:
                QMessageBox.warning(self, "오류", "OBS 연결에 실패했습니다.")
                self.error_label.setText("❌ OBS 연결에 실패했습니다.")
                self.update_record_button_style()
                return

            self.google_uploader = GoogleDriveUploader(self.settings)
            if not self.google_uploader.connected:
                QMessageBox.warning(self, "오류", "Google Drive 연결에 실패했습니다.")
                self.error_label.setText(f"❌ 구글 드라이브 연결에 실패했습니다.")
                self.update_record_button_style()
                return

            current_settings = self.dialog.get_settings()  # 최신값으로 다시 가져옴
            if not current_settings["google_folder_id"].strip():
                QMessageBox.warning(self, "오류", "Google Drive 폴더 ID가 설정되어 있지 않습니다.")
                self.error_label.setText("❌ Google Drive 폴더 ID가 비어 있습니다.")
                self.update_record_button_style()
                return

            self.error_label.setText("")
            self.update_record_button_style()
        except Exception as e:
            self.error_label.setText(f"❌ 구글 드라이브 연결에 실패했습니다.")

    def start_key_listener(self):
        def on_click(x, y, button, pressed):
            if pressed:
                print(f"Clicked at ({x}, {y}) with {button}")
                self.click_signal_handler.clicked.emit()  # UI 스레드에 전달

        def on_press(key):
            if key == keyboard.Key.left:
                # print("⬅️ 왼쪽 화살표 (이전 슬라이드)")
                self.click_signal_handler.key_pressed.emit('left')
            elif key == keyboard.Key.right:
                # print("➡️ 오른쪽 화살표 (다음 슬라이드)")
                self.click_signal_handler.key_pressed.emit('right')
            elif key == keyboard.Key.tab:
                # print("탭 키 눌림")
                self.click_signal_handler.key_pressed.emit('tab')


        # 백그라운드에서 마우스 클릭 리슨 시작
        # self.mouse_listener = mouse.Listener(on_click=on_click)
        self.key_listener = keyboard.Listener(on_press=on_press)
        self.key_listener.start()
    
    def handle_key_event(self, key_name):
        if key_name == 'left':
            self.show_usage()
        elif key_name == 'right':
            self.close_qr_dialog()
        elif key_name == 'tab':
            if self.usage_dialog == None and self.qr_dialog == None:
                self.toggle_recording()

    def _finish_after_saving(self):
        self.stop_recording()
        # self.show_qr_dialog()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

        

if __name__ == "__main__":
    main() 