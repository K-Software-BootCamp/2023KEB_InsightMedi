#%%
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("AI Labeling DICOM Viewer")
        self.setFixedSize(700, 700)

        # Create a toolbar
        toolbar = self.addToolBar("Toolbar")

        '''
        파일 도구
        '''

        # 파일 열기 버튼
        open_action = QAction(QIcon('icon/open_file_icon.png'), "파일 열기", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        # 파일 저장하기 버튼
        save_action = QAction(QIcon('icon/save_icon.png'), "저장", self)
        save_action.triggered.connect(self.save)
        toolbar.addAction(save_action)

        # 파일 다른 이름으로 저장하기 버튼
        save_as_action = QAction(QIcon('icon/save_as_icon.png'), "다른 이름으로 저장", self)
        save_as_action.triggered.connect(self.save_as)
        toolbar.addAction(save_as_action)

        toolbar.addSeparator()  # 구분선

        # 윈도잉 액션
        windowing_action = QAction(QIcon('icon/windowing_icon.png'), "윈도잉", self)
        windowing_action.triggered.connect(self.apply_windowing)
        toolbar.addAction(windowing_action)

        toolbar.addSeparator()  # 구분선

        '''
        어노테이션 도구
        '''

        # 직선 액션
        straightline_action = QAction(QIcon('icon/straightline_icon.png'), "직선", self)
        straightline_action.triggered.connect(self.draw_straight_line)
        toolbar.addAction(straightline_action)

        # 원 액션
        circle_action = QAction(QIcon('icon/circle_icon.png'), "원", self)
        circle_action.triggered.connect(self.draw_circle)
        toolbar.addAction(circle_action)

        # 사각형 액션
        rectangle_action = QAction(QIcon('icon/rectangle_icon.png'), "사각형", self)
        rectangle_action.triggered.connect(self.draw_rectangle)
        toolbar.addAction(rectangle_action)

        # 곡선 액션
        curve_action = QAction(QIcon('icon/curve_icon.png'), "곡선", self)
        curve_action.triggered.connect(self.draw_curve)
        toolbar.addAction(curve_action)

        # 자유형 액션
        freehand_action = QAction(QIcon('icon/freehand_icon.png'), "자유형", self)
        freehand_action.triggered.connect(self.draw_freehand)
        toolbar.addAction(freehand_action)

        toolbar.addSeparator()  # 구분선

        '''
        보기 도구
        '''

        # 확대 액션
        zoom_in_action = QAction(QIcon('icon/zoom_in_icon.png'), "확대", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        # 축소 액션
        zoom_out_action = QAction(QIcon('icon/zoom_out_icon.png'), "축소", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

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

    def draw_straight_line(self):
        # 직선 그리기 기능 구현
        print("Draw Straight Line")

    def draw_circle(self):
        # 원 그리기 기능 구현
        print("Draw Circle")

    def draw_rectangle(self):
        # 사각형 그리기 기능 구현
        print("Draw Rectangle")

    def draw_curve(self):
        # 곡선 그리기 기능 구현
        print("Draw Curve")

    def draw_freehand(self):
        # 자유형 그리기 기능 구현
        print("Draw Freehand")

    def zoom_in(self):
        # 확대 보기 기능 구현
        print("Zoom in")

    def zoom_out(self):
        # 축소 보기 기능 구현
        print("Zoom out")


app = QApplication(sys.argv)

window = MyWindow()
window.show()
sys.exit(app.exec_())

# %%
