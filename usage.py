from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, QSizePolicy)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt


class UsageDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("사용법")
        self.setMinimumWidth(800)
        self.setMaximumWidth(900)

        # 전체 배경 컨테이너
        central_widget = QWidget(self)
        central_widget.setStyleSheet("""
            background-color: #EBD4BC;
            border-radius: 10px;
        """)

        outer_layout = QVBoxLayout(self)
        outer_layout.addWidget(central_widget)

        # 메인 레이아웃
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        central_widget.setLayout(layout)

        # 제목 라벨
        title_label = QLabel("사용법")
        title_label.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("""
            color: #4A4A4A;
            background-color: #FCEEF3;
            padding: 10px 20px;
            border-radius: 8px;
        """)
        title_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        layout.addWidget(title_label)

        # 설명 텍스트 하나로 합치기
        usage_text = """
        <html>
            <head>
                <style>
                    p {
                        line-height: 1.8;  /* 줄 간격 조정 */
                        font-size: 20px;
                        color: #333333;
                        margin: 0 0 10px 0;
                    }
                </style>
            </head>
            <body>
                <p>1. 녹화를 준비한다</p>
                <p>2. 리모컨의 🔴 버튼을 눌러 녹화를 시작한다 <span style="font-size: 16px; color: #aaaaaa;">(최대 1분 녹화)</span></p>
                <p>3. 리모컨의 🔴 버튼을 눌러 녹화를 종료한다 <span style="font-size: 16px; color: #aaaaaa;">(1분 후 자동 종료)</span></p>
                <p>4. 잠시 뒤 나오는 QR코드를 스캔해 영상을 다운로드한다. <span style="font-size: 16px; color: #aaaaaa;">(QR 코드는 1분 출력)</span></p>
                <p>5. 녹화 파일을 확인한다.</p>
                <br/>
                <hr/>
                <br/>
                <p>❓ 영상을 다운받지 못했을 경우<br/>\t- QR 이미지 하단에 출력되는 '파일명'을 알려주세요.</p>
                <br/>
                <p style="text-align: left;">☎️ 문의: SNS 수련회 공식 카카오톡 채널 </p>
                <p style="text-align: right; font-size: 16px; color: #aaaaaa;">🔵 닫기</p>
            </body>
        </html>
        """


        # 설명 라벨을 담을 위젯
        description_container = QWidget()
        description_container.setStyleSheet("""
            background-color: #ffffff;
            border-radius: 8px;
        """)
        description_layout = QVBoxLayout()
        description_layout.setContentsMargins(20, 50, 20, 20)
        description_container.setLayout(description_layout)

        description_label = QLabel(usage_text)
        description_label.setTextFormat(Qt.TextFormat.RichText)  # HTML 사용 설정
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #333; line-height: 1.5;")
        description_label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)

        description_layout.addWidget(description_label)
        layout.addWidget(description_container)

        self.adjustSize()  # 내부 내용 기준으로 사이즈 확정
        self.move(
            self.screen().geometry().center() - self.frameGeometry().center()
        )