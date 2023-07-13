#%%
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Labeling DICOM Viewer")
        self.setFixedSize(700, 700)
        self.setWindowIcon(QIcon("GUI_icon.png"))

        menu_bar = self.menuBar()
        self.setMenuBar(menu_bar)
        menu_bar.setNativeMenuBar(False)    # MacOs에서만 필요한 코드입니다. 다른 운영체제라면 삭제하세요.

        file_menu = menu_bar.addMenu("File")

        # 파일 열기 버튼
        open_action = QAction("Open File", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # 파일 저장하기 버튼
        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save)
        file_menu.addAction(save_action)

        # 파일 다른 이름으로 저장하기 버튼
        save_as_action = QAction("Save As...", self)
        save_as_action.triggered.connect(self.save_as)
        file_menu.addAction(save_as_action)

        image_menu = menu_bar.addMenu("Image")

        windowing = QMenu("Windowing", self)

        windowing_action = QAction("Apply Windowing", self)
        windowing_action.triggered.connect(self.apply_windowing)
        windowing.addAction(windowing_action)

        image_menu.addMenu(windowing)

        annotation_menu = menu_bar.addMenu("Annotation Tool")

        draw_action = QAction("Draw", self)
        draw_action.triggered.connect(self.start_drawing)
        annotation_menu.addAction(draw_action)

        # 창 중앙 정렬
        screen_geometry = QApplication.desktop().availableGeometry()
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        self.move(center_x, center_y)

    def open_file(self):
        # 파일 열기 기능 구현
        print("Open File")

    def save(self):
        # 저장 기능 구현
        print("Save")

    def save_as(self):
        # 다른 이름으로 저장 기능 구현
        print("Save As...")

    def apply_windowing(self):
        # Windowing 적용 기능 구현
        print("Apply Windowing")

    def start_drawing(self):
        # 그리기 기능 시작
        print("Start Drawing")


app = QApplication(sys.argv)

window = MyWindow()
window.show()
sys.exit(app.exec_())

# %%
