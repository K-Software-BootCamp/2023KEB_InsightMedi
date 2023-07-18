import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer

import cv2
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
import matplotlib.pyplot as plt

from controller.control import Controller
from functools import partial
from data.dcm_data import DcmData
from module.Windowing_Inputdialog import InputDialog


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.timer = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("InsightMedi Viewer")
        # self.setFixedSize(700, 700)

        self.main_widget = QWidget()
        self.cid = None

        # DcmData Added
        self.dd = DcmData()
        self.setCentralWidget(self.main_widget)

        self.canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.cl = Controller(self.canvas, self.dd)
        self.label_list = QWidget()
        self.label_layout = QVBoxLayout()
        self.label_list.setLayout(self.label_layout)
        self.buttons = {}
        self.slider = QSlider(Qt.Horizontal)
        self.play_button = QPushButton("Play")

        # Layout
        grid_box = QGridLayout(self.main_widget)
        grid_box.addWidget(self.canvas, 0, 0)
        grid_box.addWidget(self.label_list, 0, 1)
        grid_box.addWidget(self.slider, 1, 0)
        grid_box.addWidget(self.play_button, 2, 0)

        # Create a toolbar
        toolbar = self.addToolBar("Toolbar")
        self.statusBar().showMessage("")
        '''
        파일 도구
        '''

        # 파일 열기 버튼
        open_action = QAction(
            QIcon('icon/open_file_icon.png'), "Open File", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        # 파일 저장하기 버튼
        save_action = QAction(QIcon('icon/save_icon.png'), "Save", self)
        save_action.triggered.connect(self.save)
        toolbar.addAction(save_action)

        # 파일 다른 이름으로 저장하기 버튼
        save_as_action = QAction(
            QIcon('icon/save_as_icon.png'), "Save As", self)
        save_as_action.triggered.connect(self.save_as)
        toolbar.addAction(save_as_action)

        toolbar.addSeparator()  # 구분선

        # 윈도잉 액션
        windowing_action = QAction(
            QIcon('icon/windowing_icon.png'), "Windowing", self)
        windowing_action.triggered.connect(self.windowing_input_dialog)
        toolbar.addAction(windowing_action)

        toolbar.addSeparator()  # 구분선

        self.is_panning = False
        self.pan_start = None

        '''
        어노테이션 도구
        '''

        # 직선 액션
        straightline_action = QAction(
            QIcon('icon/straightline_icon.png'), "Line", self)
        straightline_action.triggered.connect(self.draw_straight_line)
        toolbar.addAction(straightline_action)

        # 원 액션
        circle_action = QAction(QIcon('icon/circle_icon.png'), "Circle", self)
        circle_action.triggered.connect(self.draw_circle)
        toolbar.addAction(circle_action)

        # 사각형 액션
        rectangle_action = QAction(
            QIcon('icon/rectangle_icon.png'), "Rectangle", self)
        rectangle_action.triggered.connect(self.draw_rectangle)
        toolbar.addAction(rectangle_action)

        # 곡선 액션
        curve_action = QAction(QIcon('icon/curve_icon.png'), "Curve", self)
        curve_action.triggered.connect(self.draw_curve)
        toolbar.addAction(curve_action)

        # 자유형 액션
        freehand_action = QAction(
            QIcon('icon/freehand_icon.png'), "Free Hand", self)
        freehand_action.triggered.connect(self.draw_freehand)
        toolbar.addAction(freehand_action)

        eraser_action = QAction(
            QIcon('icon/eraser_icon.png'), "Eraser", self)
        eraser_action.triggered.connect(self.erase)
        toolbar.addAction(eraser_action)

        toolbar.addSeparator()  # 구분선

        '''
        보기 도구
        '''

        # 확대 액션
        zoom_in_action = QAction(
            QIcon('icon/zoom_in_icon.png'), "Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        # 축소 액션
        zoom_out_action = QAction(
            QIcon('icon/zoom_out_icon.png'), "Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        # 창 중앙 정렬
        screen_geometry = QApplication.desktop().availableGeometry()
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        self.move(center_x, center_y)

    def set_status_bar(self):
        # print(self.dd.ds)
        try:
            wl = self.dd.ds.WindowCenter
            ww = self.dd.ds.WindowWidth
            # print(wl, ww)
            self.statusBar().showMessage(f"WL: {wl} WW:{ww}")
        except AttributeError:
            self.statusBar().showMessage("")
            pass

    def open_file(self):
        # 파일 열기 기능 구현
        self.canvas.figure.clear()
        options = QFileDialog.Options()
        fname = QFileDialog.getOpenFileName(
            self, "Open File", "", "DCM Files (*.dcm *.DCM);;Video Files (*.mp4);;All Files (*)", options=options)
        if fname[0]:
            # 파일 열기
            dd = self.dd
            dd.open_file(fname)

            # viewer 설정 초기화
            self.set_status_bar()
            self.delete_label()
            self.open_label(dd.frame_label_dict)
            self.slider.setValue(0)
            self.buttons.clear() if self.buttons else None

            if dd.file_extension == "DCM" or dd.file_extension == "dcm":  # dcm 파일인 경우
                self.cl.img_show(dd.image, cmap=plt.cm.gray, init=True)
                self.slider.setMaximum(0)
                
            elif dd.file_extension == "mp4":  # mp4 파일인 경우
                self.timer = QTimer()
                self.cl.img_show(dd.image, cmap=plt.cm.gray, init=True)

                print(dd.total_frame)
                self.slider.setMaximum(dd.total_frame - 1)

                # 눈금 설정
                self.slider.setTickPosition(
                    QSlider.TicksBelow)  # 눈금 위치 설정 (아래쪽)
                self.slider.setTickInterval(10)  # 눈금 간격 설정

                self.slider.valueChanged.connect(self.sliderValueChanged)
                self.play_button.clicked.connect(self.playButtonClicked)

                # timer start
                if not self.timer:
                    self.timer = self.canvas.new_timer(interval=33)  # 30FPS
                    self.timer.add_callback(self.updateFrame)
                    self.timer.start()
            else:    # viewer에 호환되지 않는 확장자 파일
                pass
        else:
            print("Open fail")

    def open_label(self, ld):
        for frame in ld:
            # label = QLabel(label_text)
            print(frame)
            button = QPushButton(f"{frame} frame", self)
            self.buttons[frame] = button
            button.clicked.connect(partial(self.label_clicked, frame))
            # self.layout.addWidget(label)
            self.label_layout.addWidget(button)

    def delete_label(self):
        while self.label_layout.count():
            item = self.label_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.label_layout.update()

    def label_clicked(self, frame):
        if self.dd.file_extension == "mp4":
            self.dd.frame_number = frame
            self.slider.setValue(frame)
            self.updateFrame()
        self.cl.label_clicked(frame)

    def save(self):
        # 저장 기능 구현
        self.dd.save_label()

        print("Save...")

    def save_as(self):
        # 다른 이름으로 저장 기능 구현
        print("Save As...")

    def sliderValueChanged(self, value):
        print("Slider Value : ", value)
        self.dd.frame_number = value
        self.dd.video_player.set(cv2.CAP_PROP_POS_FRAMES, self.dd.frame_number)
        self.updateFrame()

    def playButtonClicked(self):
        if not self.timer.isActive():
            self.play_button.setText("Pause")
            self.timer.timeout.connect(self.updateFrame)
            self.timer.start(33)
        else:
            self.play_button.setText("Play")
            self.timer.timeout.disconnect(self.updateFrame)
            self.dd.frame_number = int(
                self.dd.video_player.get(cv2.CAP_PROP_POS_FRAMES))
            self.slider.setValue(self.dd.frame_number)
            self.timer.stop()

    def updateFrame(self):
        ret, frame = self.dd.video_player.read()
        if ret:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.cl.img_show(frame_rgb, clear=True)

    def windowing_input_dialog(self):
        # Windowing 값 입력하는 input dialog
        windowing_dialog = InputDialog()
        if windowing_dialog.exec_() == QDialog.Accepted:
            wl_value, ww_value, ok_flag = windowing_dialog.getText()

            if ok_flag:
                wl = wl_value
                ww = ww_value
                self.apply_windowing(ww, wl)

    def apply_windowing(self, ww, wl):
        # Windowing apply 구현
        dd = self.dd
        dd.ds.WindowCenter = wl
        dd.ds.WindowWidth = ww
        self.set_status_bar()
        # print(wl, ww)
        modality_lut_image = apply_modality_lut(dd.image, dd.ds)
        voi_lut_image = apply_voi_lut(modality_lut_image, dd.ds)
        # comparison = voi_lut_image == self.image
        # mismatch_count = np.count_nonzero(comparison == False)
        # print(mismatch_count)
        self.cl.img_show(voi_lut_image, cmap=plt.cm.gray, clear=True)

    def draw_straight_line(self):
        self.cl.init_draw_mode("line")

    def draw_circle(self):
        self.cl.init_draw_mode("circle")

    def draw_rectangle(self):
        self.cl.init_draw_mode("rectangle")

    def draw_curve(self):
        # 곡선 그리기 기능 구현
        pass

    def draw_freehand(self):
        # 자유형 그리기 기능 구현
        self.cl.init_draw_mode("freehand")

    def erase(self):
        # print("erase")
        reply = QMessageBox.question(self, 'Message', 'Do you erase all?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cl.erase_annotation(erase_dict=True)

    def zoom_in(self):
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        new_xlim = (current_xlim[0] * 0.9, current_xlim[1] * 0.9)
        new_ylim = (current_ylim[0] * 0.9, current_ylim[1] * 0.9)

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        self.set_mpl_disconnect()
        self.set_mpl_connect(self.on_pan_mouse_press,
                             self.on_pan_mouse_move, self.on_pan_mouse_release)
        self.canvas.draw()

    def on_pan_mouse_press(self, event):  # zoom in 상태에서 화면 이동
        if event.button == 1 and not self.is_panning:
            self.is_panning = True
            self.pan_start = (event.x, event.y)

    def on_pan_mouse_move(self, event):
        if self.is_panning:
            x_diff = event.x - self.pan_start[0]
            y_diff = event.y - self.pan_start[1]

            current_xlim = self.ax.get_xlim()
            current_ylim = self.ax.get_ylim()

            new_xlim = (current_xlim[0] - x_diff, current_xlim[1] - x_diff)
            new_ylim = (current_ylim[0] - y_diff, current_ylim[1] - y_diff)

            image_width = self.ds.pixel_array.shape[1]
            image_height = self.ds.pixel_array.shape[0]

            # DICOM 이미지 경계 안에서 화면 이동하는지 확인
            if new_xlim[0] >= 0 and new_xlim[1] <= image_width:
                self.ax.set_xlim(new_xlim)

            if new_ylim[0] >= 0 and new_ylim[1] <= image_height:
                self.ax.set_ylim(new_ylim)

            self.pan_start = (event.x, event.y)
            self.canvas.draw()

    def on_pan_mouse_release(self, event):
        if event.button == 1 and self.is_panning:
            self.is_panning = False

    def zoom_out(self):
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        new_xlim = (current_xlim[0] * 1.1, current_xlim[1] * 1.1)
        new_ylim = (current_ylim[0] * 1.1, current_ylim[1] * 1.1)

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        self.canvas.draw()


app = QApplication(sys.argv)

window = MyWindow()
window.show()
sys.exit(app.exec_())
