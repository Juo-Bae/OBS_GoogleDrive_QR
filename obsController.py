import sys

from obsws_python.reqs import ReqClient
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QHBoxLayout, QMessageBox)
from PyQt6.QtCore import Qt, QRect, QTimer
from PyQt6.QtGui import QIcon, QFont

class OBSController:
    def __init__(self, host="localhost", port=4455, password=""):
        try:
            self.ws = ReqClient(host=host, port=port, password=password)
            self.connected = True
            print("✅ OBS WebSocket 연결 성공")
        except Exception as e:
            print(f"❌ OBS WebSocket 연결 실패: {e}")
            self.connected = False

        self.record_directory = self.ws.get_record_directory().record_directory
        print(f"✅ 녹화 디렉토리: {self.record_directory}")
        
    def start_recording(self):
        if self.connected:
            try:
                self.ws.start_record()
                print("▶️ 녹화 시작")
                return True
            except Exception as e:
                print(f"❌ 녹화 시작 실패: {e}")
        return False

    def stop_recording(self):
        if self.connected:
            try:
                self.ws.stop_record()
                print("⏹️ 녹화 중지")
                return True
            except Exception as e:
                print(f"❌ 녹화 중지 실패: {e}")
        return False

    def close(self):
        if self.connected:
            self.ws.disconnect()


