import copy
import matplotlib.pyplot as plt
import numpy as np
import cv2
import math

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
from data.dcm_data import DcmData


class Controller():
    def __init__(self, dd: DcmData, canvas: FigureCanvas, set_status_bar, delete_label_button) -> None:
        self.canvas = canvas
        self.dd = dd
        self.fig = canvas.figure
        self.ax = self.fig.add_subplot(111, aspect = 'auto')

        # canvas fig 색상 변경
        self.fig.patch.set_facecolor('#303030')
        self.ax.patch.set_facecolor("#3A3A3A")
        self.ax.tick_params(axis = 'x', colors = 'gray')
        self.ax.tick_params(axis = 'y', colors = 'gray')

        self.annotation_mode = None
        self.annotation = None
        self.selector_mode = None
        self.cid = []

        self.start = None
        self.end = None
        self.points = []
        self.is_drawing = False
        self.is_panning = False
        self.pan_Start = None
        self.change_status_bar = set_status_bar
        self.delete_label_button = delete_label_button

        self.press=None
        self.artist = None
        self.changed_coor = None
        
    def draw_annotation(self, color="red"):
        if self.start and self.end and self.selector_mode == "Drawing":
            if self.annotation:
                #연속적인 라벨의 그림을 보여주기 위해 이전 annotation을 제거해줍니다.
                if self.annotation_mode == 'freehand':
                    # print(dir(self.annotation))
                    self.annotation[0].remove()
                else:
                    self.annotation.remove()    

            self.dd.set_new_label_name()
            label_class = self.dd.label_name
            
            if self.annotation_mode == "line":
                x = [self.start[0], self.end[0]]
                y = [self.start[1], self.end[1]]
                self.annotation = self.ax.plot(x, y, picker=True, label=label_class, color=color)[0]
                if self.is_drawing is False:
                    self.dd.add_label("line", ((x[0], y[0]), (x[1], y[1])), color)

            elif self.annotation_mode == "rectangle":
                width = abs(self.start[0] - self.end[0])
                height = abs(self.start[1] - self.end[1])
                x = min(self.start[0], self.end[0])
                y = min(self.start[1], self.end[1])
                self.annotation = self.ax.add_patch(
                    Rectangle((x, y), width, height, fill=False, picker=True, label=label_class, edgecolor=color))
                if self.is_drawing is False:
                    self.dd.add_label("rectangle", (x, y, width, height), color)

            elif self.annotation_mode == "circle":
                dx = self.end[0] - self.start[0]
                dy = self.end[1] - self.start[1]
                center = self.start
                radius = np.sqrt(dx ** 2 + dy ** 2)
                self.annotation = self.ax.add_patch(
                    Circle(center, radius, fill=False, picker=True, label=label_class, edgecolor=color))
                if self.is_drawing is False:
                    self.dd.add_label("circle", (center, radius), color)

            elif self.annotation_mode == "freehand":
                x, y = zip(*self.points)
                self.annotation = self.ax.plot(x, y, picker=True, label=label_class, color=color)
                if self.is_drawing is False:
                    self.points = []
                    self.dd.add_label("freehand", self.points, color)

            elif self.annotation_mode == "windowing":
                dd = self.dd
                dx = self.end[0] - self.start[0]
                dy = self.end[1] - self.start[1]

                # if dd.file_mode == 'mp4':
                #     self.mp4_windowing_change(dd, dx, dy)
                if dd.file_mode == 'dcm':
                    self.dcm_windowing_change(dd, dx, dy)
            self.canvas.draw()

    def set_mpl_connect(self, *args):
        """다음순서로 args받아야 합니다. button_press_event, motion_notify_event, button_release_event"""
        cid1 = self.canvas.mpl_connect('button_press_event', args[0])
        cid2 = self.canvas.mpl_connect('motion_notify_event', args[1])
        cid3 = self.canvas.mpl_connect('button_release_event', args[2])
        self.cid = [cid1, cid2, cid3]


    def set_mpl_disconnect(self):
        if self.cid:
            for cid in self.cid:
                self.canvas.mpl_disconnect(cid)
        self.cid = []

    def draw_init(self):
        self.start = None
        self.end = None
        self.is_drawing = False
        self.annotation = None
        self.selector_mode = "Drawing"
        self.change_status_bar()
        self.set_mpl_disconnect()
        if self.annotation_mode == "freehand":
            self.points = []
            self.set_mpl_connect(self.on_mouse_press,
                                 self.on_freehand_mouse_move, self.on_mouse_release)
        else:
            self.set_mpl_connect(self.on_mouse_press,
                                 self.on_mouse_move, self.on_mouse_release)

    def init_zoom_mode(self, mode):
        self.set_mpl_disconnect()
        cid4 = self.canvas.mpl_connect('button_press_event', self.on_pan_mouse_press)
        cid5 = self.canvas.mpl_connect('motion_notify_event', self.on_pan_mouse_move)
        cid6 = self.canvas.mpl_connect('button_release_event', self.on_pan_mouse_release)
        self.cid = [cid4, cid5, cid6]

    def init_draw_mode(self, mode):
        # 직선 그리기 기능 구현
        print(mode)
        self.annotation_mode = mode
        self.draw_init()
        # status bar변경하는 함수 포인터를 Vierwer_Gui로부터 받아오기

    def init_selector(self, mode):
        self.set_mpl_disconnect()
        if mode =="delete":
            # if self.artist:
            #     #선택된 artist가 있고 버튼을 누르면 지웁니다.
            #     self.artist.remove()
            #     self.canvas.draw()
            print("in the init selecotr mode delelte")
            self.selector_mode = 'selector'
            self.annotation_mode = mode
            cid4 = self.canvas.mpl_connect('key_press_event', self.selector_key_on_press)
            self.cid.append(cid4)
        elif mode == 'selector':
            self.selector_mode = mode
            self.annotation_mode = None
        self.change_status_bar()
        
        cid0 = self.canvas.mpl_connect('pick_event', self.selector_on_pick)
        cid1 = self.canvas.mpl_connect('button_press_event', self.selector_on_press)
        cid2 = self.canvas.mpl_connect('motion_notify_event', self.selector_on_move)
        cid3 = self.canvas.mpl_connect('button_release_event', self.selector_on_release)
        
        self.cid.extend([cid0, cid1, cid2, cid3])
        # print(self.cid)
    
    def selector_on_pick(self, event):
        # print(dir(event))
        #기존의 선택된 artist의 색깔을 원상태인 빨간색으로 바꿔줍니다.
        if self.artist is not None and event.artist != self.artist:
            self.selector_change_color("red")

        if self.selector_mode == 'selector':
            #현재 선택된 artist를 self.artist로 저장시켜 다른 함수에서 접근 가능하게 합니다. 
            self.artist = event.artist
            self.selector_change_color("blue")
            # print(dir(self.artist))
            print(f"label name : {self.artist.get_label()}")
            if self.annotation_mode == 'delete':
                try:
                    self.artist = event.artist
                    self.delete_label(self.artist.get_label())
                    self.artist.remove()
                    #label button과 frame_label_dict에서 해당 라벨 삭제
                    # self.dd.frame_label_dict[self.dd.frame_number][self.dd.label_class].delete()
                    # self.dd.delete_label_file
                except AttributeError as e:
                    print(e)
        self.canvas.draw()
    
    
    def delete_label(self, label_name):
        """ contorls > Viewer_GUI > dcm_data순으로 먼저 버튼을 지우고 데이터 지우는 순차적 구조입니다."""
        self.delete_label_button(label_name)
        
    def selector_on_press(self, event):
        """ 라벨들 선택하면 self.press에 x,y 데이터 저장하는 기능입니다. """
        if self.artist is None:
            return
        if event.inaxes != self.artist.axes:
            return
        contains, attrd = self.artist.contains(event)
        if not contains:
            return
        if isinstance(self.artist, Line2D):
            xdata= self.artist.get_xdata()
            ydata= self.artist.get_ydata()
            
        elif isinstance(self.artist, Rectangle):
            xdata, ydata = self.artist.xy
        
        elif isinstance(self.artist, Circle):
            xdata, ydata = self.artist.get_center()
        else:
            return
        
        self.press = (xdata, ydata), (event.xdata, event.ydata)
        print(self.press)

    def selector_on_move(self, event):
        """마우스로 드래그하면 self.artist를 움직일 수 있게 합니다."""

        if self.press is None:
            return

        (x0, y0), (xpress, ypress) = self.press
        dx = event.xdata - xpress
        dy = event.ydata - ypress
        
        if isinstance(self.artist, Line2D):
            self.artist.set_xdata(x0 + dx)
            self.artist.set_ydata(y0 + dy)
        elif isinstance(self.artist, Rectangle):
            # print(f'x0={x0}, xpress={xpress}, event.xdata={event.xdata}, '
            #       f'dx={dx}, x0+dx={x0+dx}')
            self.artist.set_x(x0 + dx)
            self.artist.set_y(y0 + dy)
        elif isinstance(self.artist, Circle):
            self.artist.set_center((x0 + dx, y0 + dy))
            
        self.changed_coor = (x0 + dx, y0 + dy)
        self.canvas.draw()

    def selector_on_release(self, event):
        self.canvas.draw()
        self.modify_label_data()
        

    def modify_label_data(self):
        cc = self.changed_coor
        print("MODIFY _ LABEL _ DATA")
        print(cc)
        ret_points = None
        if isinstance(self.artist, Line2D):
            #free hand
            print(len(cc[0]))
            print(cc[0][0], cc[1][0])
            ret_points = [(cc[0][i], cc[1][i]) for i in range(len(cc[0]))]
        elif isinstance(self.artist, Rectangle):
            ret_points = (cc[0], cc[1], self.artist.get_width(), self.artist.get_height())

        elif isinstance(self.artist, Circle):
            ret_points = (self.artist.get_center(), self.artist.get_radius())
            
            
        print(ret_points)
            
        print("MODIFY _ LABEL _ END")
        self.dd.modify_label_data(self.artist.get_label(), ret_points)
        self.press = None

    def selector_key_on_press(self, event):
        print(event.key)
        print(dir(event))
        if event.key == "delete":
            print("delete press")

    def selector_change_color(self, color):
        if isinstance(self.artist, Line2D):
            self.artist.set_color(color)
        else:
            self.artist.set_edgecolor(color)

    def on_mouse_press(self, event):
        if event.button == 1:
            self.is_drawing = True
            self.start = (event.xdata, event.ydata)

    def on_mouse_move(self, event):
        if self.is_drawing:
            self.end = (event.xdata, event.ydata)
            self.draw_annotation()

    def on_mouse_release(self, event):
        if event.button == 1:
            self.is_drawing = False
            self.end = (event.xdata, event.ydata)
            self.draw_annotation()
            self.annotation = None

    def on_freehand_mouse_move(self, event):
        if self.is_drawing:
            self.end = (event.xdata, event.ydata)
            if self.end not in self.points:
                self.points.append(self.end)
                self.draw_annotation()

    def label_clicked(self, frame):
        self.erase_annotation()
        self.dd.load_label_dict()
        frame_directory = self.dd.frame_label_dict[frame]

        for drawing_type in frame_directory:
            label_directory = frame_directory[drawing_type]
            for label in label_directory:
                ld = label_directory[label]
                #print("\nld:", ld)
                if drawing_type == "line":
                    coor = ld["coords"]
                    color = ld["color"]
                    self.ax.plot((coor[0], coor[2]), (coor[1], coor[3]), picker=True, color=color)
                    
                if drawing_type == "rectangle":
                    coor = ld["coords"]
                    color = ld["color"]
                    #print("현재 label은 사각형임", ld['rectangle'])
                    self.ax.add_patch(Rectangle((coor[0], coor[1]), coor[2], coor[3], fill=False,
                                                    picker=True, edgecolor=color))
                if drawing_type == "circle":
                    coor = ld["coords"]
                    color = ld["color"]
                    self.ax.add_patch(
                        Circle(coor[0], coor[1], fill=False, picker=True, edgecolor=color))
                    
                if drawing_type == "freehand":
                    fh = ld["coords"]
                    color = ld["color"]
                    for coor in fh:
                        x_coords, y_coords = zip(*fh)
                        self.ax.plot(
                            x_coords, y_coords, picker=True, color=color)
            
        self.canvas.draw()

    def img_show(self, img, cmap='viridis', init=False, clear=False):
        if init:
            self.ax = self.canvas.figure.subplots()
        if clear:
            self.ax.clear()
        self.ax.imshow(img, cmap=cmap)
        self.ax.tick_params(axis = 'x', colors = 'gray')
        self.ax.tick_params(axis = 'y', colors = 'gray')
        self.canvas.draw()

    def erase_annotation(self, erase_dict=False):
        for patch in self.ax.patches:
            patch.remove()
        for patch in self.ax.lines:
            patch.remove()
        self.canvas.draw()

        if erase_dict:
            if self.dd.frame_number in self.dd.frame_label_dict:
                del self.dd.frame_label_dict[self.dd.frame_number]
            #self.dd.frame_label_dict[self.dd.frame_number] = copy.deepcopy(
            #    self.dd.label_dict_schema)
            print("초기화된 frame_label_dict", self.dd.frame_label_dict)

    def mp4_windowing_change(self, dd: DcmData, dx: float, dy: float):
        pass
        
        # print(type(frame)) : ndarray
        # print(frame.shape) : (720, 1280, 3)
        # print(b, g, r)
        # dd.video_wl = round(dd.video_wl + dx, 2)
        # dd.video_ww = round(dd.video_ww - dy, 2)
        # print(dd.video_wl, dd.video_ww)
        # # cv2.convertScaleAbs(frame, frame, alpha=(255.0 / dd.video_ww), beta=(dd.video_wl - dd.video_ww / 2))
        # frame = self.frame_apply_windowing(dd, dd.image)
        # self.change_status_bar()
        # # print(type(frame))
        # self.img_show(frame, clear=True)

    def frame_apply_windowing(self, dd, frame):
        pass
        # b, g, r = cv2.split(frame)
        # r = cv2.convertScaleAbs(r, alpha=abs(255 / dd.video_wl), beta=(dd.video_wl - dd.video_ww / 2))
        # g = cv2.convertScaleAbs(g, alpha=abs(255 / dd.video_wl), beta=(dd.video_wl - dd.video_ww / 2))
        # b = cv2.convertScaleAbs(b, alpha=abs(255 / dd.video_wl), beta=(dd.video_wl - dd.video_ww / 2))
        # return cv2.merge((b, g, r))
        
    def dcm_windowing_change(self, dd, dx, dy):
        """
        windwow center는 x값에 대해 변경되므로 마우스 좌우로 변경됩니다.  
        windwow width는 y값에 대해 변경되므로 마우스 상하로 변경됩니다.
        windowing 값은 정수값입니다.
        """
        def digit_length(num):
            return int(math.log10(num)) + 1 if num > 0 else 0
        xd = digit_length(dd.image.shape[0]) - 1
        yd = digit_length(dd.image.shape[1]) - 1
        try:
            dd.ds.WindowCenter = int(dd.ds.WindowCenter + (10**xd) * dx / dd.image.shape[0])
            dd.ds.WindowWidth = int(dd.ds.WindowWidth - (10**yd) * dy / dd.image.shape[1])
            # print(wl, ww)
            modality_lut_image = apply_modality_lut(dd.image, dd.ds)
            voi_lut_image = apply_voi_lut(modality_lut_image, dd.ds)
            # comparison = voi_lut_image == self.image
            # mismatch_count = np.count_nonzero(comparison == False)
            # print(mismatch_count)
            self.change_status_bar()
            self.img_show(voi_lut_image, cmap=plt.cm.gray, clear=True)
        except AttributeError:
            dd.ds.WindowCenter = 256
            dd.ds.WindowWidth = 256
            #del self.dd.frame_label_dict[self.dd.frame_number]

    def zoom_in(self):
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        new_xlim = (current_xlim[0] * 0.9, current_xlim[1] * 0.9)
        new_ylim = (current_ylim[0] * 0.9, current_ylim[1] * 0.9)

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        self.canvas.draw()

    def on_pan_mouse_press(self, event):
        if event.button == 1 and not self.is_panning:
            self.is_panning = True
            self.pan_start = (event.x, event.y)
            print("on_pan_mouse_press")

    def on_pan_mouse_move(self, event):
        if self.is_panning:
            x_diff = event.x - self.pan_start[0]
            y_diff = event.y - self.pan_start[1]

            current_xlim = self.ax.get_xlim()
            current_ylim = self.ax.get_ylim()

            new_xlim = (current_xlim[0] - x_diff, current_xlim[1] - x_diff)
            new_ylim = (current_ylim[0] - y_diff, current_ylim[1] - y_diff)

            self.ax.set_xlim(new_xlim)
            self.ax.set_ylim(new_ylim)

            self.pan_start = (event.x, event.y)
            self.canvas.draw()
            print("on_pan_mouse_move")

    def on_pan_mouse_release(self, event):
        if event.button == 1 and self.is_panning:
            self.is_panning = False
            print("on_pan_mouse_release")

    def zoom_out(self):
        current_xlim = self.ax.get_xlim()
        current_ylim = self.ax.get_ylim()

        new_xlim = (current_xlim[0] * 1.1, current_xlim[1] * 1.1)
        new_ylim = (current_ylim[0] * 1.1, current_ylim[1] * 1.1)

        self.ax.set_xlim(new_xlim)
        self.ax.set_ylim(new_ylim)

        self.canvas.draw()
