# 문제점 1 => 해결 x 
# 이미지 교체해도 예전 이미지가 계속 나오거나 앱이 멈춘 것과 같이 작동이 원활하지 않음
# 원인 : QWebEngineView가 결과를 갱신하지 않음
# 동일한 HTML 문자열이 다시 로드될 때 무시되는 경우인데, 특히 이미지 Base64가 같으면 생겨요.
from PyQt5.QtCore import QCoreApplication 

# 문제점 2 => 둘 다 사용, 어느 정도 해결
# 파일명이 달라도 연속으로 같은 확장자의 이미지를 선택하면, PyQt / PIL 또는 캐시 시스템이 같은 파일로 인식해서 이미지가 갱신되지 않는 현상이야
# 방법 1 : PIL 이미지 로딩 시 강제 캐시 무시 (재로딩) 
 #방법 2 : 웹뷰 html을 강제로 갱신하기 (랜덤 쿼리 붙이기)
 # html 내부 이미지 태그에 무작위 요소를 추가 

# 문제점 3 - 
# 이미지 4번 이상 교체하면 앱이 멈춘다. 
# 실제로 PyQt5 + QWebEngineView를 쓸 때 자주 발생하는 구조적인 문제야.
# 원인 : Base64 인코딩 이미지가 커서: 메모리 급증 → 브라우저 캐시 부담
# 해결 방법 
# 기존 QWebEngineView를 재사용하고 force-refresh만 하도록 변경
# self.webview_img를 새로 만들지 않고, setHtml()로 계속 덮어쓰기
# base64 이미지 캐시 우회를 위해 <img> 태그에 쿼리 스트링 추가 (?v=uuid)
# setHtml() 전에 기존 HTML과 다르게 강제로 바뀌도록 내용에 더미 값을 삽입

# 문제점 4 => 해결 완료 
# 위의 해결방식은 이미지가 깨져서 나온다. base64로 인코딩된 데이터가 html에 잘못 삽입되거나 쿼리스트링이였던 v=uuid가 
# base64 문자열 뒤에 붙어서 이미지가 제대로 인식되지 않기 때문이다. 
# 결론 base64 데이터는 쿼리스트링 붙일 수 없다. 
# 해결 제안 : body안에 <div id="uuid"> 등 랜덤값 추가로 캐시 회피 처리

# 문제점 5 = 만화, 아이콘, 캐릭터(단일 객체)는 imageNet에 없으므로 분류가 안 될 가능성이 높다. 
# resnet18 같은 ImageNet 사전 학습 모델은 1000개 일반 클래스(주로 실세계사진)만 분류할 수 있다. 
# 시계로 시간 재는 사람 손이 있는 아이콘도 객체 분류 가능했음 
# 해결 : custom dataset(캐릭터, 만화, 아이콘 등)으로 파인튜닝(재학습)이 필요하다. 

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView

from PIL import Image
import torchvision.transforms as transforms
import torchvision.models as models
import torch
import torch.nn.functional as F

# QtWebEngine 캐시 관련 오류 (액세스 거부) 해결하기 
# 웹 엔진이 gpu 캐시를 저장하는 폴더 권한 문제로, 관리자 권한으로 실행해서 해결한다. 
# 혹은 아래와 같이 임시 경로를 사용하도록 설정해 권한 문제를 우회할 수 있다. 
import os
os.environ["QTWEBENGINE_DISABLE_GPU"] = "1"
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--no-sandbox"


import io
import base64

import urllib.request

# ImageNet 클래스 이름 로딩
IMAGENET_CLASS_INDEX = None
with urllib.request.urlopen("https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt") as f:
    IMAGENET_CLASS_INDEX = [line.decode("utf-8").strip() for line in f.readlines()]

# 모델 준비 (CPU 기준, eval 모드)
# 최신 토치비전 버전에서는 deprecated되었으므로 weights 파라미터를 써야한다. 
from torchvision.models import resnet18, ResNet18_Weights
# model = models.resnet18(pretrained=True)
model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
model.eval()

# 이미지 전처리 함수
def preprocess_image(img_path):
    with open(img_path, 'rb') as f:
        img_bytes = io.BytesIO(f.read())  # ✅ 캐시 우회

    input_image = Image.open(img_path).convert("RGB")
    preprocess = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406], 
            std=[0.229, 0.224, 0.225]),
    ])
    input_tensor = preprocess(input_image)
    input_batch = input_tensor.unsqueeze(0)  # batch 차원 추가
    return input_batch, input_image

# 이미지 분류 예측
def predict_image(img_path):
    input_batch, pil_img = preprocess_image(img_path)
    with torch.no_grad():
        output = model(input_batch)
        probs = F.softmax(output[0], dim=0)
    top5_prob, top5_catid = torch.topk(probs, 5)
    results = []
    for i in range(top5_prob.size(0)):
        results.append((IMAGENET_CLASS_INDEX[top5_catid[i]], float(top5_prob[i])))
    return pil_img, results


# PIL 이미지 -> base64 인코딩 (HTML에 넣기 위함)
def pil_image_to_base64(pil_img):
    buff = io.BytesIO()
    pil_img.save(buff, format="PNG")
    img_str = base64.b64encode(buff.getvalue()).decode("utf-8")
    return img_str

import uuid
# 이미지 분류 결과 HTML 생성 - 문제점 4 해결 
def make_image_report_html(pil_img, predictions):
    img_base64 = pil_image_to_base64(pil_img)
    random_id = uuid.uuid4() 

    html = f"""
    <html><head><meta charset="utf-8"><title>이미지 분류 결과</title></head><body>
    <h2>이미지 분류 결과</h2>
    <img src="data:image/png;base64,{img_base64}" width="300"><br><br>
    <div id="rand">{random_id}</div>  <!-- 캐시 우회용 랜덤 텍스트 -->
    <table border="1" cellpadding="5" style="border-collapse: collapse;">
    <tr><th>클래스</th><th>확률</th></tr>
    """
    for cls, prob in predictions:
        html += f"<tr><td>{cls}</td><td>{prob*100:.2f}%</td></tr>"
    html += "</table></body></html>"
    return html

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("[gayoon choi] 이미지 분류기")

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.btn_load_img = QPushButton("이미지 불러오기")
        layout.addWidget(self.btn_load_img)
        self.btn_load_img.clicked.connect(self.load_image)

        self.lbl_img_path = QLabel("선택된 이미지: 없음")
        layout.addWidget(self.lbl_img_path)

        self.btn_predict = QPushButton("분류 예측 실행")
        layout.addWidget(self.btn_predict)
        self.btn_predict.clicked.connect(self.predict_image_clicked)
        self.btn_predict.setEnabled(False)

        self.webview_img = QWebEngineView()
        layout.addWidget(self.webview_img)

        self.current_img_path = None

    def load_image(self):
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self, "이미지 파일 선택", "",
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*)", options=options)
        if file_path:
            self.current_img_path = file_path
            self.lbl_img_path.setText(f"선택된 이미지: {file_path}")
            self.btn_predict.setEnabled(True)


    def predict_image_clicked(self):
        if not self.current_img_path:
            return
        pil_img, preds = predict_image(self.current_img_path)
        html = make_image_report_html(pil_img, preds)
        self.webview_img.setHtml(html)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.resize(900, 700)
    win.show()
    sys.exit(app.exec_())
