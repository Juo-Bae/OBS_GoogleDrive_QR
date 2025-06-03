from PyQt6.QtWidgets import QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
import os
import qrcode

def generate_qr(file_name, download_url, base_folder):
    # QR 폴더 경로 생성
    qr_folder = os.path.join(base_folder, "QR")
    os.makedirs(qr_folder, exist_ok=True)

    # 타임스탬프 기반 파일명 생성
    qr_filename = f"qr_{file_name}.png"
    qr_path = os.path.join(qr_folder, qr_filename)

    # QR 생성 및 저장
    qr = qrcode.make(download_url)
    qr.save(qr_path)
    
    return qr_path

class QRDialog(QDialog):
    closed = pyqtSignal()

    def __init__(self, qr_image_path, timeout_seconds=30, parent=None):
        super().__init__(parent)

        self.parent = parent

        self.setWindowTitle("다운로드")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        self.setStyleSheet("background-color: #EBD4BC;")
        self.timeout = timeout_seconds
        self.remaining_time = timeout_seconds

        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 타이틀    
        title_label = QLabel("🎥 영상 다운로드")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Arial", 32))
        title_label.setStyleSheet("color: #333333;")
        layout.addWidget(title_label)

        # 이미지
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setPixmap(QPixmap(qr_image_path).scaled(
            300, 300,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        ))
        layout.addWidget(image_label)

        self.file_name = os.path.basename(qr_image_path).replace(".png", "").replace("qr_", "")

        # 텍스트 라벨 (HTML 적용)
        self.html_label = QLabel()
        self.html_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.html_label.setTextFormat(Qt.TextFormat.RichText)
        self.html_label.setFont(QFont("Arial", 12))
        layout.addWidget(self.html_label)

        self.setLayout(layout)
        self.update_html()

        # 타이머
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(1000)

    def update_html(self):
        self.html_label.setText(f"""
        <div style="text-align: center; font-family: Arial;">
            <div style="font-size: 20px; margin: 10px 0; color: #333333;">
                <b style="color:#000000;">{self.file_name}</b>
            </div>
            <div style="font-size: 18px; color: #555555; margin-top: 20px;">
                <p>⏳ 잠시 뒤 창이 닫힙니다</p>
                <p style="font-size: 32px; font-weight: bold; color: #333333; margin-top: 10px;">{self.remaining_time}초</p>
            </div>
            <div style="font-size: 16px; color: #777777; margin-top: 50px;">
                🟢 창 닫기
            </div>
        </div>
        """)

    def update_countdown(self):
        if self.remaining_time > 0:
            self.remaining_time -= 1
            self.update_html()
        else:
            self.timer.stop()
            self.close()  # ✅ accept() 대신 close()


    def closeEvent(self, event):
        print("📌 QRDialog closed")
        self.closed.emit()  # 시그널 보냄
        super().closeEvent(event)