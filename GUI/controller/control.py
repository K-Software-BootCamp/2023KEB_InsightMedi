import copy
import matplotlib.pyplot as plt
import numpy as np
import cv2

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.patches import Circle, Rectangle
from matplotlib.lines import Line2D
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
from data.dcm_data import DcmData


class Controller():
    def __init__(self, dd: DcmData, canvas: FigureCanvas) -> None:
        self.canvas = canvas
        self.dd = dd
        self.fig = canvas.figure
        self.ax = self.fig.add_subplot(111, aspect = 'auto')

        # canvas fig 색상 변경
        self.fig.patch.set_facecolor('#303030')
        self.ax.tick_params(axis = 'x', colors = 'gray')
        self.ax.tick_params(axis = 'y', colors = 'gray')

        self.annotation_mode = None
        self.selector_mode = None
        self.cid = []

        self.start = None
        self.end = None
        self.points = []
        self.is_drawing = False
        self.is_panning = False
        self.pan_Start = None

        self.press=None
        self.artist = None
        
    def draw_annotation(self):
        if self.start and self.end and self.is_drawing == False:
            label_name = self.dd.label_name
            if self.annotation_mode == "line":
                x = [self.start[0], self.end[0]]
                y = [self.start[1], self.end[1]]
                self.ax.plot(x, y, picker=True, label=label_name, color='red')[0]
                self.dd.add_label("line", (x[0], y[0], x[1], y[1]))

            elif self.annotation_mode == "rectangle":
                width = abs(self.start[0] - self.end[0])
                height = abs(self.start[1] - self.end[1])
                x = min(self.start[0], self.end[0])
                y = min(self.start[1], self.end[1])
                self.ax.add_patch(
                    Rectangle((x, y), width, height,  fill=False, picker=True, label=label_name, edgecolor='red') )
                self.dd.add_label("rectangle", (x, y, width, height))

            elif self.annotation_mode == "circle":
                dx = self.end[0] - self.start[0]
                dy = self.end[1] - self.start[1]
                center = self.start
                radius = np.sqrt(dx ** 2 + dy ** 2)
                self.ax.add_patch(
                    Circle(center, radius, fill=False, picker=True, label=label_name, edgecolor='red'))
                self.dd.add_label("circle", (center, radius))

            elif self.annotation_mode == "freehand":
                if self.points:
                    x, y = zip(*self.points)
                    self.ax.plot(x, y, picker=True, label=label_name, color='red')
                    self.end = None
                    self.dd.add_label("freehand", self.points)

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
        self.func = None
        self.press = None
        if self.cid:
            for cid in self.cid:
                self.canvas.mpl_disconnect(cid)
        self.cid = []

    def draw_init(self):
        self.start = None
        self.end = None
        self.is_drawing = False
        self.set_mpl_disconnect()
        if self.annotation_mode == "freehand":
            self.points = []
            self.set_mpl_connect(self.on_mouse_press,
                                 self.on_freehand_mouse_move, self.on_mouse_release)
        else:
            self.set_mpl_connect(self.on_mouse_press,
                                 self.on_mouse_move, self.on_mouse_release)

    def initie_zoom_mode(self, mode):
        self.set_mpl_disconnect()
        cid4 = self.canvas.mpl_connect('button_press_event', self.on_pan_mouse_press)
        cid5 = self.canvas.mpl_connect('motion_notify_event', self.on_pan_mouse_move)
        cid6 = self.canvas.mpl_connect('button_release_event', self.on_pan_mouse_release)
        self.cid = [cid4, cid5, cid6]

    def init_draw_mode(self, mode, func=None):
        # 직선 그리기 기능 구현
        print(mode)
        self.annotation_mode = mode
        self.draw_init()
        if func:
            self.func = func

    def init_selector(self, mode):
        self.set_mpl_disconnect()
        self.selector_mode = mode
        if mode =="delete":
            # if self.artist:
            #     #선택된 artist가 있고 버튼을 누르면 지웁니다.
            #     self.artist.remove()
            #     self.canvas.draw()
            cid4 = self.canvas.mpl_connect('key_press_event', self.selector_key_on_press)
            self.cid.append(cid4)
        cid0 = self.canvas.mpl_connect('pick_event', self.selector_on_pick)
        cid1 = self.canvas.mpl_connect('button_press_event', self.selector_on_press)
        cid2 = self.canvas.mpl_connect('motion_notify_event', self.selector_on_move)
        cid3 = self.canvas.mpl_connect('button_release_event', self.selector_on_release)
        self.cid.extend([cid1, cid2, cid3])
        print(self.cid)
    
    def selector_on_pick(self, event):
        print(dir(event))
        #기존의 선택된 artist의 색깔을 원상태인 빨간색으로 바꿔줍니다.
        if event.artist != self.artist:
                try:
                    if isinstance(self.artist, Line2D):
                        self.artist.set_color('red')
                    else:
                        self.artist.set_edgecolor('red')
                except AttributeError:
                    pass

        if self.selector_mode == 'delete':
            try:
                event.artist.remove()
                #label button과 frame_label_dict에서 해당 라벨 삭제
                # self.dd.frame_label_dict[self.dd.frame_number][self.dd.label_name].delete()
                # self.dd.delete_label_file
            except AttributeError:
                pass
        elif self.selector_mode == 'selector':
            #현재 선택된 artist를 self.artist로 저장시켜 다른 함수에서 접근 가능하게 합니다. 
            self.artist = event.artist
            
            # print(dir(self.artist))         
            if isinstance(self.artist, Line2D):
                print("Line select")
                self.artist.set_color('blue')
            else:
                self.artist.set_edgecolor('blue')
            print(self.press)
            print(f"label name : {self.artist.get_label()}")
        self.canvas.draw()
    
    def selector_on_press(self, event):
        if event.inaxes != self.artist.axes:
            return
        contains, attrd = self.artist.contains(event)
        if not contains:
            return
        print('event contains', self.artist.xy)
        self.press = self.artist.xy, (event.xdata, event.ydata)
        print(self.press)
        # print(dir(event))

    def selector_on_move(self, event):
        """Move the rectangle if the mouse is over us."""
        try:
            if self.press is None or event.inaxes != self.artist.axes:
                return
        except AttributeError:
            return
        if isinstance(self.artist, Line2D):
            pass

        elif isinstance(self.artist, Rectangle):
            (x0, y0), (xpress, ypress) = self.press
            dx = event.xdata - xpress
            dy = event.ydata - ypress
            # print(f'x0={x0}, xpress={xpress}, event.xdata={event.xdata}, '
            #       f'dx={dx}, x0+dx={x0+dx}')
            self.artist.set_x(x0+dx)
            self.artist.set_y(y0+dy)
        self.canvas.draw()

    def selector_on_release(self, event):
        self.press = None
        self.canvas.draw()


    def selector_key_on_press(self, event):
        print(event)
        if event == "delete":
            print("delete press")

        
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

    def on_freehand_mouse_move(self, event):
        if self.is_drawing:
            self.end = (event.xdata, event.ydata)
            if self.end not in self.points:
                self.points.append(self.end)
                self.draw_annotation()

    def label_clicked(self, frame):
        self.erase_annotation()
        self.dd.load_label_dict()
        ld = self.dd.frame_label_dict[frame]
        if ld["line"]:
            line = ld["line"]
            for coor in line:
                self.ax.plot((coor[0], coor[2]), (coor[1], coor[3]), picker=True, color='red')
        if ld["rectangle"]:
            rec = ld["rectangle"]
            for coor in rec:
                self.ax.add_patch(Rectangle((coor[0], coor[1]), coor[2], coor[3], fill=False,
                                            picker=True, edgecolor='red'))
        if ld["circle"]:
            cir = ld["circle"]
            for coor in cir:
                self.ax.add_patch(
                    Circle(coor[0], coor[1], fill=False, picker=True, edgecolor='red'))
        if ld["freehand"]:
            freehand = ld["freehand"]
            for fh in freehand:
                for coor in fh:
                    x_coords, y_coords = zip(*fh)
                    self.ax.plot(
                        x_coords, y_coords, picker=True, color='red')
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
        # self.func()
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
        """
        try:
            dd.ds.WindowCenter = round(dd.ds.WindowCenter + dx, 2)
            dd.ds.WindowWidth = round(dd.ds.WindowWidth - dy, 2)
            # print(wl, ww)
            modality_lut_image = apply_modality_lut(dd.image, dd.ds)
            voi_lut_image = apply_voi_lut(modality_lut_image, dd.ds)
            # comparison = voi_lut_image == self.image
            # mismatch_count = np.count_nonzero(comparison == False)
            # print(mismatch_count)
            self.func()
            self.img_show(voi_lut_image, cmap=plt.cm.gray, clear=True)
        except AttributeError:
            dd.ds.WindowCenter = 200
            dd.ds.WindowWidth = 200
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
