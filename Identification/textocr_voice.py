# 신분증 인식 시스템, 
# 신분증에서 텍스트와 사진 분류 불가하면, 음성 인식으로 2차 인증

# 문제점 1 - 등록할 이미지 파일명이 영어여야 한다. 예) 신분증1.png (x)  / id1.png(o)
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QFileDialog, QTextEdit
from PyQt5.QtCore import Qt
import easyocr

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("신분증 인식 및 음성 인증")
        self.resize(400, 300)

        self.layout = QVBoxLayout()

        self.label = QLabel("신분증 이미지 선택 후 인식")
        self.layout.addWidget(self.label)

        self.btn_load = QPushButton("신분증 이미지 선택")
        self.btn_load.clicked.connect(self.load_image)
        self.layout.addWidget(self.btn_load)

        self.result_text = QTextEdit()
        self.layout.addWidget(self.result_text)

        self.btn_voice_auth = QPushButton("음성 인증으로 넘어가기")
        self.btn_voice_auth.clicked.connect(self.open_voice_auth)
        self.btn_voice_auth.setVisible(False)  # 기본 숨김
        self.layout.addWidget(self.btn_voice_auth)

        self.setLayout(self.layout)

        # EasyOCR reader 초기화 (한국어+영어)
        self.reader = easyocr.Reader(['ko', 'en'])

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "", "Image Files (*.png *.jpg *.jpeg)")
        if not file_path:
            return

        self.result_text.clear()
        self.label.setText("텍스트 추출 중...")
        self.btn_voice_auth.setVisible(False)

        # OCR 수행
        results = self.reader.readtext(file_path, detail=0)

        if results:
            text = "\n".join(results)
            self.result_text.setText(text)
            self.label.setText("신분증 인식 성공!")
        else:
            self.label.setText("텍스트 인식 실패. 음성 인증으로 넘어가세요.")
            self.btn_voice_auth.setVisible(True)

    def open_voice_auth(self):
        self.voice_window = VoiceAuthWindow()
        self.voice_window.show()

class VoiceAuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("음성 인증")
        self.resize(300, 200)

        layout = QVBoxLayout()
        label = QLabel("여기에 음성 인증 기능 구현")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)

        self.setLayout(layout)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec_())
