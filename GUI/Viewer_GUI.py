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
        self.setGeometry(100,100,1280,720)
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

        for i in range(10):
            self.button_layout = QHBoxLayout()
            label_name = "label %d"%(i+1)
            self.label_button = QPushButton(label_name)
            self.label_button.setStyleSheet("color: gray; height: 30px; width: 120px;")
            self.label_button.clicked.connect(partial(self.label_button_clicked, label_name))

            self.go_button = QPushButton("GO")
            self.go_button.setStyleSheet("color: gray; height: 30px; width: 50px;")
            self.go_button.clicked.connect(partial(self.go_button_clicked, label_name))

            self.button_layout.addWidget(self.label_button)
            self.button_layout.addWidget(self.go_button)
            self.label_layout.addLayout(self.button_layout)
            
            self.label_go_buttons = [self.label_button, self.go_button]
            self.buttons[label_name] = self.label_go_buttons

        # print(self.buttons)
        
        # slider and play button
        self.slider = QSlider(Qt.Horizontal)
        self.play_button = QPushButton("Play")
        self.play_button.setStyleSheet("color: lightgray;")
        self.video_status = None

        # Label list scroll area
        self.label_scroll_area = QScrollArea()
        self.label_scroll_area.setWidget(self.label_list)
        self.label_scroll_area.setWidgetResizable(True)

        # Layout
        grid_box = QGridLayout(self.main_widget)
        grid_box.setColumnStretch(0, 4)   # column 0 width 2
        grid_box.setColumnStretch(1, 1)   # column 1 width 1

        #column 0
        grid_box.addWidget(self.canvas, 0, 0, 4, 1)
        grid_box.addWidget(self.slider, 4, 0)

        # column 1
        grid_box.addWidget(self.label_scroll_area, 0, 1, 2, 1)
        grid_box.addWidget(self.play_button, 2, 1)

        # Create a toolbar
        toolbar = self.addToolBar("Toolbar")
        # toolbar.setStyleSheet("background-color: #303030;")
        self.statusBar().showMessage("")

        #Create Controller
        self.cl = Controller(self.dd, self.canvas, self)
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

        cursor_action = QAction(
            QIcon('icon/cursor_icon.png'), "Selector", self)
        cursor_action.triggered.connect(self.selector)
        toolbar.addAction(cursor_action)

        palette_action = QAction(
            QIcon('icon/palette_icon.png'), "Palette", self)
        palette_action.triggered.connect(self.palette)
        toolbar.addAction(palette_action)
        
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

        # Freehand action
        freehand_action = QAction(
            QIcon('icon/freehand_icon.png'), "Free Hand", self)
        freehand_action.triggered.connect(self.draw_freehand)
        toolbar.addAction(freehand_action)

        # delete action
        delete_action = QAction(
            QIcon('icon/delete_icon.png'), "Delete", self)
        delete_action.triggered.connect(self.delete)
        toolbar.addAction(delete_action)
        
        # delete all action
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
            self.video_status = None
            self.dd.video_player.release()

    def set_status_bar(self):
        # print(self.dd.ds)
        sm = self.cl.selector_mode
        am = self.cl.annotation_mode
        smam = f"Tool Status : {sm}:{am}" if am else f"Tool Status : {sm}"
        try:
            if self.dd.file_mode == 'dcm':
                wl = self.dd.ds.WindowCenter
                ww = self.dd.ds.WindowWidth
                # print(wl, ww)
                self.statusBar().showMessage(f"WL: {wl} WW:{ww} {smam}")
            elif self.dd.file_mode == 'mp4':
                vs = self.video_status
                self.statusBar().showMessage(f"Video Stauts: {vs} "
                                            f"Frame: {self.dd.frame_number} / {self.dd.total_frame} {smam}")
        except (AttributeError, TypeError):
            self.statusBar().showMessage(smam)
            
    def open_file(self):
        # 파일 열기 기능 구현
        self.canvas.figure.clear()
        self.release_resources()
        
        self.setCursor(Qt.ArrowCursor)
        options = QFileDialog.Options()
        fname = QFileDialog.getOpenFileName(
            self, "Open File", "", "DCM Files (*.dcm *.DCM);;Video Files (*.mp4);;All Files (*)", options=options)
        
        if fname[0]:
            # 파일 열기
            dd = self.dd
            dd.open_file(fname)
            # viewer 설정 초기화
            
            #self.delete_total_label()   # frame layout에 추가된 button widget 전체 삭제
            self.slider.setValue(0)    # slider value 초기화
            # TODO : load label 함수 수정 후 아래 코드 주석 풀기
            #self.load_label_button(dd.frame_label_dict)   # open한 파일에 이미 저장되어 있는 label button 활성화하는 함수

            if dd.file_mode == "dcm":  # dcm 파일인 경우
                self.cl.img_show(dd.image, cmap=plt.cm.gray, init=True)
                self.slider.setMaximum(0)
                
            elif dd.file_mode == "mp4":  # mp4 파일인 경우
                self.timer = QTimer()
                self.cl.img_show(dd.image, cmap=plt.cm.gray, init=True)

                print(dd.total_frame)
                self.slider.setMaximum(dd.total_frame - 1)
                self.video_status = "Ready"
                # 눈금 설정
                self.slider.setTickPosition(
                    QSlider.TicksBelow)  # 눈금 위치 설정 (아래쪽)
                self.slider.setTickInterval(10)  # 눈금 간격 설정

                self.slider.valueChanged.connect(self.sliderValueChanged)
                self.play_button.clicked.connect(self.playButtonClicked)

            else:    # viewer에 호환되지 않는 확장자 파일
                print("Not accepted file format")

            self.set_status_bar()    # 현재 windwoing 상태 초기화
        else:
            print("Open fail")

    def load_label_button(self, ld):    # frame_label_dict에 있는 label 정보 반영하기
        #print(ld)
        for frame, frame_dict in ld.items():
            for drawing_type, label_dict in frame_dict.itmes():
                for label_name in label_dict.keys():
                    if label_name in self.buttons:
                        button_list = self.buttons[label_name]
                        button_list[0].setStyleSheet("color: white; font-weight: bold; height: 30px; width: 120px;")
                        button_list[1].setStyleSheet("color: white; font-weight: bold; height: 30px; width: 50px;")

    
    def label_button_clicked(self, label):
        button_list = self.buttons[label]
        button_list[0].setStyleSheet("color: white; font-weight: bold; height: 30px; width: 120px;")
        button_list[1].setStyleSheet("color: white; font-weight: bold; height: 30px; width: 50px;")
        print(label, 'button clicked')
        
        # TODO : 해당 label을 frame에서 지운 후, label 하나 그리면 그리기 모드 종료되고, 해당 label 선택된 상태로 만들기 
        # (일단 사각형 그리기로 했는데, 추후 수정이 필요합니다)
        # if self.dd.frame_label_check(label):
        # 사각형 1개 그리고 나면 selector 모드로 바뀌어야 함

        if self.dd.frame_label_check(self.dd.frame_number):
            self.dd.delete_label(label)
            self.cl.erase_annotation(label)

        if self.cl.annotation_mode == "line":
            self.draw_straight_line(label)
        elif self.cl.annotation_mode == "circle":
            self.draw_circle(label)
        elif self.cl.annotation_mode == "freehand":
            self.draw_freehand(label)
        else:
            self.draw_rectangle(label) 
        self.dd.delete_label(label)
        self.cl.erase_annotation(label)

    def go_button_clicked(self, label):
        print(label, "go button clicked")

        found_label = False

        for frame, frame_dict in self.dd.frame_label_dict.items():
            for drawing_type, label_dict in frame_dict.items():
                if label in label_dict.keys():
                    first_frame = frame
                    found_label = True
                    break
            if found_label == True:
                break
        
        if found_label:
            self.label_clicked(first_frame, label)
            print("go button 누른 후 현재 frame number", self.dd.frame_number)
            print("frame_label_check 함수 확인:", self.dd.frame_label_check(self.dd.frame_number))

    def disable_total_label(self):
        #frame 이동 버튼들 전부 제거하기
        for _label_name in self.buttons:
            button_list = self.buttons[_label_name]
            button_list[0].setStyleSheet("color: gray; font-weight: normal; height: 30px; width: 120px;")
            button_list[1].setStyleSheet("color: gray; font-weight: normal; height: 30px; width: 50px;")
            self.dd.delete_label(_label_name)
        self.label_layout.update()
            
        #data에서 해당 라벨이름 정보 제거하기
    
    def delete_frame_button(self, frame):
        # FIXME : 특정 frame에 있는 label들 비활성화 화기
        if frame in self.buttons:
            #button_to_remove = self.buttons[frame]
            #self.label_layout.removeWidget(button_to_remove)
            #button_to_remove.deleteLater()
            del self.buttons[frame]
            print(f"{frame} 프레임에 대한 버튼 제거됨")
        else:
            print(f"{frame} 프레임에 대한 버튼을 찾을 수 없음")
        self.label_layout.update()

    def disable_label_button(self, _label_name):
        #특정 label 버튼 볼드체 풀기
        if _label_name in self.buttons:
            button_list = self.buttons[_label_name]
            button_list[0].setStyleSheet("color: gray; font-weight: normal; height: 30px; width: 120px;")
            button_list[1].setStyleSheet("color: gray; font-weight: normal; height: 30px; width: 50px;")
            print(self.buttons)
            print(f"{_label_name} 라벨에 대한 버튼 비활성화됨")
        else:
            print(f"{_label_name} 라벨에 대한 버튼을 찾을 수 없음")
        self.label_layout.update()
            
        #data에서 해당 라벨이름 정보 제거하기
        self.dd.delete_label(_label_name)
    
    def label_clicked(self, frame, label):
        #label 버튼 클릭시 frame값을 전달받고 이동 후 label들을 보여줍니다.
        self.setCursor(Qt.ArrowCursor)
        if self.dd.file_mode == "mp4":
            self.dd.frame_number = frame
            self.slider.setValue(frame)
            
        self.cl.label_clicked(frame, label)

    def save(self):
        # 저장 기능 구현
        self.dd.save_label()

        print("Save...")

    def save_as(self):
        # 다른 이름으로 저장 기능 구현
        print("Save As...")

    def sliderValueChanged(self, value):   # 슬라이더로 frame 위치 조정
        if not self.timer.isActive():
            #print("slider value changed 함수 호출")
            #print("Slider Value : ", value)
            self.dd.frame_number = value
            #print("현재 frame: ", self.dd.frame_number)
            self.dd.video_player.set(cv2.CAP_PROP_POS_FRAMES, self.dd.frame_number)
            self.updateFrame()
        elif self.timer.isActive() and value != self.dd.frame_number:
            #print("Slider 클릭함!!!!!!")
            #print('바뀐 value:', value)
            self.dd.frame_number = value
            self.dd.video_player.set(cv2.CAP_PROP_POS_FRAMES, self.dd.frame_number)

    def playButtonClicked(self):    # 영상 재생 버튼의 함수
        self.setCursor(Qt.ArrowCursor)
        if not self.timer:    # timer 없으면 새로 생성하고 updateFrame을 callback으로 등록
            self.timer = self.canvas.new_timer(interval=16)  # 60FPS
            #self.timer.add_callback(self.updateFrame)
      
        if not self.timer.isActive():   # 재생 시작
            self.play_button.setText("Pause")
            self.video_status = 'Playing'
            self.timer.start()
            self.timer.timeout.connect(self.updateFrame)
            self.timer.start(16)
        else:    # timer가 활성화되면 정지
            self.play_button.setText("Play")
            self.timer.timeout.disconnect(self.updateFrame)
            self.video_status = 'Stop'
            self.set_status_bar()
            self.timer.stop()
            self.dd.frame_number = int(
                self.dd.video_player.get(cv2.CAP_PROP_POS_FRAMES)) - 1
            #self.slider.setValue(self.dd.frame_number)
            

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
                #print("재생 중")
                self.slider.setValue(self.dd.frame_number)
        print("update Frame 호출, 현재 frame: ", self.dd.frame_number)
        
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
        self.setCursor(Qt.ArrowCursor)
        self.cl.init_selector("selector")
    
    def palette(self):
        color = QColorDialog.getColor()
        if color.isValid():
            # 선택한 색상이 유효한 경우, 해당 색상 정보를 저장
            self.selected_color = color
            print(self.selected_color)

    def delete(self):
        self.setCursor(Qt.PointingHandCursor)
        self.cl.init_selector("delete")

    def apply_windowing(self):
        self.setCursor(Qt.OpenHandCursor)
        self.cl.init_draw_mode("windowing")

    def draw_straight_line(self, label=None):
        if label:
            self.setCursor(Qt.CrossCursor)
            self.cl.init_draw_mode("line", label)
        else:
            self.cl.annotation_mode = "line"
            draw_reply = QMessageBox.information(self, 'Message', 'Click label button before drawing')
    
    def draw_circle(self, label=None):
        if label:
            self.setCursor(Qt.CrossCursor)
            self.cl.init_draw_mode("circle", label)
        else:
            self.cl.annotation_mode = "circle"
            draw_reply = QMessageBox.information(self, 'Message', 'Click label button before drawing')

    def draw_rectangle(self, label=None):
        if label:
            self.setCursor(Qt.CrossCursor)
            self.cl.init_draw_mode("rectangle", label)
        else:
            self.cl.annotation_mode = "rectangle"
            draw_reply = QMessageBox.information(self, 'Message', 'Click label button before drawing')

    def draw_freehand(self, label=None):
        # 자유형 그리기 기능 구현
        if label:
            self.setCursor(Qt.CrossCursor)
            self.cl.init_draw_mode("freehand")
        else:
            self.cl.annotation_mode = "freehand"
            draw_reply = QMessageBox.information(self, 'Message', 'Click label button before drawing')

    def delete_all(self):
        self.setCursor(Qt.ArrowCursor)
        # print("erase")
        reply = QMessageBox.question(self, 'Message', 'Do you erase all?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.cl.erase_all_annotation()    # canvas 위에 그려진 label 삭제
            self.disable_total_label()

    def zoom_in(self):
        self.cl.init_zoom_mode("in")

    def zoom_out(self):
        self.cl.init_zoom_mode("out")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()
