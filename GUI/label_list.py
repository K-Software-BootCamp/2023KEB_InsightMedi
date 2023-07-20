import sys
from PyQt5.QtWidgets import QGridLayout, QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QScrollArea, QSizePolicy

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Canvas and Button List Example")
        self.setGeometry(100, 100, 800, 600)

        # 왼쪽에 흰색 canvas 화면을 그릴 QWidget 생성
        self.canvas_widget = QWidget()
        self.canvas_widget.setStyleSheet("background-color: white;")

        # 오른쪽에는 QLabel 위젯들을 담을 QVBoxLayout과 QWidget 생성
        self.scroll_widget = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_widget)
        
        # 예시로 20개의 QLabel 위젯 생성 및 추가
        for i in range(1, 21):
            label = QLabel(f"Button {i}")
            label.setStyleSheet("border: 1px solid black; padding: 5px;")
            label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            label.mousePressEvent = lambda event, index=i: self.label_clicked(index)
            self.scroll_layout.addWidget(label)

        # QLabel 위젯들이 담긴 QWidget을 QScrollArea에 추가
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)

        # QWidget들을 grid layer로 배치하기 위한 QGridLayout 생성
        self.grid_layout = QGridLayout()
        self.grid_layout.addWidget(self.canvas_widget, 0, 0)
        self.grid_layout.addWidget(self.scroll_area, 0, 1)

        # QGridLayout을 QMainWindow의 central widget으로 설정
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.grid_layout)
        self.setCentralWidget(self.central_widget)

    def label_clicked(self, index):
        # 이 함수에서 해당 frame으로 이동하는 작업을 수행
        print(f"Moving to frame {index}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWindow()
    window.show()
    sys.exit(app.exec_())
