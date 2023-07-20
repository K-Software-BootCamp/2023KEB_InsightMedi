import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import Qt, QTimer

import cv2
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure

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
        self.main_widget.setStyleSheet("background-color: #303030;")
        self.cid = None

        # DcmData Added
        self.dd = DcmData()
        
        self.setCentralWidget(self.main_widget)

        self.canvas = FigureCanvas(Figure(figsize=(4, 3)))
        
        self.label_list = QWidget()
        self.label_layout = QVBoxLayout()
        self.label_list.setLayout(self.label_layout)
        self.buttons = {}
        self.slider = QSlider(Qt.Horizontal)
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet("color: lightgray;")

        # Layout
        grid_box = QGridLayout(self.main_widget)
        grid_box.addWidget(self.canvas, 0, 0)
        grid_box.addWidget(self.label_list, 0, 1)
        grid_box.addWidget(self.slider, 1, 0)
        grid_box.addWidget(self.play_button, 2, 0)

        # Create a toolbar
        toolbar = self.addToolBar("Toolbar")
        # toolbar.setStyleSheet("background-color: #303030;")
        self.statusBar().showMessage("")

        #Create Controller
        self.cl = Controller(self.dd, self.canvas)
        '''
        파일 도구
        '''

        # Open file action
        open_action = QAction(
            QIcon('icon/open_file_icon.png'), "Open File", self)
        open_action.triggered.connect(self.open_file)
        toolbar.addAction(open_action)

        # Save file action
        save_action = QAction(QIcon('icon/save_icon.png'), "Save", self)
        save_action.triggered.connect(self.save)
        toolbar.addAction(save_action)

        # Save file as action
        save_as_action = QAction(
            QIcon('icon/save_as_icon.png'), "Save As", self)
        save_as_action.triggered.connect(self.save_as)
        toolbar.addAction(save_as_action)

        toolbar.addSeparator()  # 구분선

        # Windowing action
        windowing_action = QAction(
            QIcon('icon/windowing_icon.png'), "Windowing", self)
        windowing_action.triggered.connect(self.apply_windowing)
        toolbar.addAction(windowing_action)

        toolbar.addSeparator()  # 구분선

        self.is_panning = False
        self.pan_start = None

        cursor_action = QAction(
            QIcon('icon/cursor_icon.png'), "Selector", self)
        cursor_action.triggered.connect(self.selector)
        toolbar.addAction(cursor_action)

        # Line action
        straightline_action = QAction(
            QIcon('icon/straightline_icon.png'), "Line", self)
        straightline_action.triggered.connect(self.draw_straight_line)
        toolbar.addAction(straightline_action)

        # Circle action
        circle_action = QAction(QIcon('icon/circle_icon.png'), "Circle", self)
        circle_action.triggered.connect(self.draw_circle)
        toolbar.addAction(circle_action)

        # Rectangle action
        rectangle_action = QAction(
            QIcon('icon/rectangle_icon.png'), "Rectangle", self)
        rectangle_action.triggered.connect(self.draw_rectangle)
        toolbar.addAction(rectangle_action)

        # Curve action
        curve_action = QAction(QIcon('icon/curve_icon.png'), "Curve", self)
        curve_action.triggered.connect(self.draw_curve)
        toolbar.addAction(curve_action)

        # Freehand action
        freehand_action = QAction(
            QIcon('icon/freehand_icon.png'), "Free Hand", self)
        freehand_action.triggered.connect(self.draw_freehand)
        toolbar.addAction(freehand_action)

        delete_action = QAction(
            QIcon('icon/delete_icon.png'), "Delete", self)
        delete_action.triggered.connect(self.delete)
        toolbar.addAction(delete_action)
        
        delete_all_action = QAction(
            QIcon('icon/delete_all_icon.png'), "Delete All", self)
        delete_all_action.triggered.connect(self.delete_all)
        toolbar.addAction(delete_all_action)

        toolbar.addSeparator()  # 구분선

        # Zoom in action
        zoom_in_action = QAction(
            QIcon('icon/zoom_in_icon.png'), "Zoom In", self)
        zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(zoom_in_action)

        # Zoom out action
        zoom_out_action = QAction(
            QIcon('icon/zoom_out_icon.png'), "Zoom Out", self)
        zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(zoom_out_action)

        # 창 중앙 정렬
        screen_geometry = QApplication.desktop().availableGeometry()
        center_x = (screen_geometry.width() - self.width()) // 2
        center_y = (screen_geometry.height() - self.height()) // 2
        self.move(center_x, center_y)

    def closeEvent(self, event):
        # mainWindow종료시 할당된 메모리 해제하기
        self.release_resources()
        event.accept()
        
    def release_resources(self):
        #동영상 플레이어 메모리 해제
        print("release resource")
        if self.dd.video_player:
            self.dd.video_player.release()

    def set_status_bar(self):
        # print(self.dd.ds)
        if self.dd.file_mode == 'dcm':
            try:
                wl = self.dd.ds.WindowCenter
                ww = self.dd.ds.WindowWidth
                # print(wl, ww)
                self.statusBar().showMessage(f"WL: {wl} WW:{ww}")
            except AttributeError:
                self.statusBar().showMessage("")
        elif self.dd.file_mode == 'mp4':
            try:
                # print(wl, ww)
                self.statusBar().showMessage(f"Frame: {self.dd.frame_number} / {self.dd.total_frame}")
            except AttributeError:
                self.statusBar().showMessage("")
            
    def open_file(self):
        # 파일 열기 기능 구현
        self.canvas.figure.clear()
        self.release_resources()
        options = QFileDialog.Options()
        fname = QFileDialog.getOpenFileName(
            self, "Open File", "", "DCM Files (*.dcm *.DCM);;Video Files (*.mp4);;All Files (*)", options=options)
        if fname[0]:
            # 파일 열기
            dd = self.dd
            dd.open_file(fname)

            # viewer 설정 초기화
            self.set_status_bar()    # 현재 windwoing 상태 초기화
            self.delete_total_label()   # label layout에 추가된 button widget 전체 삭제
            self.slider.setValue(0)    # slider value 초기화
            self.buttons.clear() if self.buttons else None   # 생성된 button widget들이 있는 dictionary 초기화
            self.open_label(dd.frame_label_dict)   # open한 파일에 이미 저장되어 있는 label button 생성

            if dd.file_mode == "dcm":  # dcm 파일인 경우
                self.cl.img_show(dd.image, cmap=plt.cm.gray, init=True)
                self.slider.setMaximum(0)
                
            elif dd.file_mode == "mp4":  # mp4 파일인 경우
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
                print("Not accepted file format")
        else:
            print("Open fail")

    def open_label(self, ld):    # label dictionary로부터 존재하는 label file만큼 버튼 생성
        for frame in ld:
            # label = QLabel(label_text)
            #print("현재 GUI에 있는 button 목록:", self.buttons)
            if frame not in self.buttons:
                button = QPushButton(f"{frame} frame", self)
                button.setStyleSheet("color: lightgray;")
                self.buttons[frame] = button
                button.clicked.connect(partial(self.label_clicked, frame))
            # self.layout.addWidget(label)
                self.label_layout.addWidget(button)

    def delete_total_label(self):
        #label이동 버튼들 전부 제거하기
        while self.label_layout.count():
            item = self.label_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
        self.label_layout.update()
    
    def delete_label(self, frame):
        #특정 frame이동 버튼 제거하기
        if frame in self.buttons:
            button_to_remove = self.buttons[frame]
            self.label_layout.removeWidget(button_to_remove)
            button_to_remove.deleteLater()
            del self.buttons[frame]
            print(f"{frame} 프레임에 대한 버튼 제거됨")
        else:
            print(f"{frame} 프레임에 대한 버튼을 찾을 수 없음")
        self.label_layout.update()

    def label_clicked(self, frame):
        #label 버튼 클릭시 frame값을 전달받고 이동 후 label들을 보여줍니다.
        if self.dd.file_mode == "mp4":
            self.dd.frame_number = frame
            self.slider.setValue(frame)
            self.updateFrame()
        elif self.dd.file_mode == 'dcm':
            #dcm 파일은 frame number 0값의 라벨 버튼이 존재.
            self.cl.label_clicked(frame)

    def save(self):
        # 저장 기능 구현
        self.dd.save_label()
        self.open_label(self.dd.frame_label_dict)

        print("Save...")

    def save_as(self):
        # 다른 이름으로 저장 기능 구현
        print("Save As...")

    def sliderValueChanged(self, value):   # 슬라이더로 frame 위치 조정
        #print("Slider Value : ", value)
        self.dd.frame_number = value
        #print("현재 frame: ", self.dd.frame_number)
        self.dd.video_player.set(cv2.CAP_PROP_POS_FRAMES, self.dd.frame_number)
        self.updateFrame()

    def playButtonClicked(self):    # 영상 재생 버튼의 함수
        if not self.timer.isActive():   # 재생 시작
            self.play_button.setText("Pause")
            self.timer.timeout.connect(self.updateFrame)
            self.timer.start(33)
        else:
            self.play_button.setText("Play")
            self.timer.timeout.disconnect(self.updateFrame)
            self.dd.frame_number = int(
                self.dd.video_player.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            self.slider.setValue(self.dd.frame_number)
            self.timer.stop()

    def updateFrame(self):    # frame update
        ret, frame = self.dd.video_player.read()
        if ret:
            self.dd.frame_number = int(
                    self.dd.video_player.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            self.set_status_bar()  # frame 상태창 변경
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.cl.img_show(rgb_frame, clear=True)

            #frame에 라벨이 존재하면 라벨을 보여줍니다.
            if self.dd.frame_number in self.dd.frame_label_dict:
                self.cl.label_clicked(self.dd.frame_number)
            
            if self.timer.isActive():
                self.slider.setValue(self.dd.frame_number)
        print("현재 frame: ", self.dd.frame_number)

        
    # windowing값을 input dialog로 받아 보여주는 코드
    # def windowing_input_dialog(self):
        # Windowing 값 입력하는 input dialog
        # windowing_dialog = InputDialog()
        # if windowing_dialog.exec_() == QDialog.Accepted:
        #     wl_value, ww_value, ok_flag = windowing_dialog.getText()

        #     if ok_flag:
        #         wl = wl_value
        #         ww = ww_value
        #         self.apply_windowing(ww, wl)
        
    def selector(self):
        self.cl.init_selector("selector")

    def delete(self):
        self.cl.init_selector("delete")

    def apply_windowing(self):
        self.cl.init_draw_mode("windowing", self.set_status_bar)

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

    def delete_all(self):
        # print("erase")
        reply = QMessageBox.question(self, 'Message', 'Do you erase all?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cl.erase_annotation(erase_dict=True)    # canvas 위에 그려진 label 삭제
            self.delete_label(self.dd.frame_number)    # button 삭제하기
            self.dd.delete_label_file(self.dd.frame_number)    # label이 저장된 text file 삭제
            print(self.dd.frame_label_dict)

    def zoom_in(self):
        self.cl.initie_zoom_mode("in")

    def zoom_out(self):
        self.cl.initie_zoom_mode("out")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
