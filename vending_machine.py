
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGridLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt

class VendingMachineApp(QWidget):
    def __init__(self):
        super().__init__()

        # 음료 정보: 이름, 가격, 이미지 파일, 재고
        self.drinks = [
            {'name': '칠성사이다', 'price': 1700, 'image': 'menu1.jpg', 'stock': 10},
            {'name': '코카콜라', 'price': 1700, 'image': 'menu2.jpg', 'stock': 10},
            {'name': '펩시 제로', 'price': 1600, 'image': 'menu3.jpg', 'stock': 10},
            {'name': '스프라이트', 'price': 1600, 'image': 'menu4.jpg', 'stock': 10},
        ]
        
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Gemini Vending Machine')
        
        main_layout = QVBoxLayout()
        grid_layout = QGridLayout()

        self.buttons = []
        self.stock_labels = []

        # 음료 메뉴 UI 생성
        for idx, drink in enumerate(self.drinks):
            # VBox for each item
            vbox = QVBoxLayout()
            vbox.setAlignment(Qt.AlignCenter)

            # 1. 음료 이미지
            pixmap = QPixmap(drink['image'])
            img_label = QLabel()
            img_label.setPixmap(pixmap.scaled(120, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
            img_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(img_label)

            # 2. 음료 이름
            name_label = QLabel(drink['name'])
            name_label.setFont(QFont('Malgun Gothic', 12, QFont.Bold))
            name_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(name_label)

            # 3. 음료 가격
            price_label = QLabel(f"{drink['price']}원")
            price_label.setFont(QFont('Malgun Gothic', 11))
            price_label.setAlignment(Qt.AlignCenter)
            vbox.addWidget(price_label)
            
            # 4. 재고 표시
            stock_label = QLabel(f"재고: {drink['stock']}개")
            stock_label.setFont(QFont('Malgun Gothic', 10))
            stock_label.setAlignment(Qt.AlignCenter)
            self.stock_labels.append(stock_label)
            vbox.addWidget(stock_label)

            # 5. 선택 버튼
            button = QPushButton('선택')
            button.setFont(QFont('Malgun Gothic', 11, QFont.Bold))
            # lambda의 i=idx 트릭을 사용하여 현재의 idx 값을 캡처
            button.clicked.connect(lambda checked, i=idx: self.select_drink(i))
            self.buttons.append(button)
            vbox.addWidget(button)
            
            grid_layout.addLayout(vbox, 0, idx)

        main_layout.addLayout(grid_layout)
        
        # 상태 메시지 라벨
        self.status_label = QLabel('음료를 선택해주세요.')
        self.status_label.setFont(QFont('Malgun Gothic', 12))
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)
        self.setGeometry(300, 300, 800, 450)

    def select_drink(self, index):
        drink = self.drinks[index]

        if drink['stock'] > 0:
            drink['stock'] -= 1
            
            # 재고 라벨 업데이트
            self.stock_labels[index].setText(f"재고: {drink['stock']}개")
            
            # 상태 메시지 업데이트
            self.status_label.setText(f"{drink['name']}을(를) 선택했습니다. (남은 재고: {drink['stock']}개)")

            if drink['stock'] == 0:
                button = self.buttons[index]
                button.setText('선택 불가')
                button.setEnabled(False)
                self.status_label.setText(f"{drink['name']}은(는) 품절입니다.")
        # 재고가 0인 경우, 버튼은 이미 비활성화되어 있으므로 별도 처리가 필요 없음

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = VendingMachineApp()
    ex.show()
    sys.exit(app.exec_())
