import copy
import matplotlib.pyplot as plt
import numpy as np
import cv2

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.patches import Circle, Rectangle
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut
from data.dcm_data import DcmData


class Controller():
    def __init__(self, dd: DcmData, canvas: FigureCanvas) -> None:
        self.canvas = canvas
        self.dd = dd
        self.ax = None

        self.annotation_mode = None
        self.cid = None

        self.start = None
        self.end = None
        self.points = []
        self.is_drawing = None

    def draw_annotation(self):
        if self.start and self.end and self.is_drawing == False:
            if self.annotation_mode == "line":
                x = [self.start[0], self.end[0]]
                y = [self.start[1], self.end[1]]
                self.ax.plot(x, y, color='red')[0]
                self.dd.add_label("line", (x[0], y[0], x[1], y[1]))

            elif self.annotation_mode == "rectangle":
                width = abs(self.start[0] - self.end[0])
                height = abs(self.start[1] - self.end[1])
                x = min(self.start[0], self.end[0])
                y = min(self.start[1], self.end[1])
                self.ax.add_patch(
                    Rectangle((x, y), width, height, fill=False, edgecolor='red'))
                self.dd.add_label("rectangle", (x, y, width, height))

            elif self.annotation_mode == "circle":
                dx = self.end[0] - self.start[0]
                dy = self.end[1] - self.start[1]
                center = self.start
                radius = np.sqrt(dx ** 2 + dy ** 2)
                self.ax.add_patch(
                    Circle(center, radius, fill=False, edgecolor='red'))
                self.dd.add_label("circle", (center, radius))

            elif self.annotation_mode == "freehand":
                if self.points:
                    x, y = zip(*self.points)
                    self.ax.plot(x, y, color='red')
                    self.end = None
                    self.dd.add_label("freehand", self.points)

            elif self.annotation_mode == "windowing":
                dd = self.dd
                dx = self.end[0] - self.start[0]
                dy = self.end[1] - self.start[1]

                if dd.file_mode == 'mp4':
                    self.mp4_windowing_change(dd, dx, dy)
                elif dd.file_mode == 'dcm':
                    self.dcm_windowing_change(dd, dx, dy)
                else:
                    print("Unexpected file format")

            self.canvas.draw()

    def set_mpl_connect(self, *args):
        """다음순서로 args받아야 합니다. button_press_event, motion_notify_event, button_release_event"""
        cid1 = self.canvas.mpl_connect('button_press_event', args[0])
        cid2 = self.canvas.mpl_connect('motion_notify_event', args[1])
        cid3 = self.canvas.mpl_connect('button_release_event', args[2])
        self.cid = [cid1, cid2, cid3]

    def set_mpl_disconnect(self):
        self.func = None
        if self.cid:
            c = self.cid
            self.canvas.mpl_disconnect(c[0])
            self.canvas.mpl_disconnect(c[1])
            self.canvas.mpl_disconnect(c[2])

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

    def init_draw_mode(self, mode, func=None):
        # 직선 그리기 기능 구현
        print(mode)
        self.annotation_mode = mode
        self.draw_init()
        if func:
            self.func = func

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
                self.ax.plot(
                    (coor[0], coor[2]), (coor[1], coor[3]), color='red')
        if ld["rectangle"]:
            rec = ld["rectangle"]
            for coor in rec:
                self.ax.add_patch(
                    Rectangle((coor[0], coor[1]), coor[2], coor[3], fill=False, edgecolor='red'))
        if ld["circle"]:
            cir = ld["circle"]
            for coor in cir:
                self.ax.add_patch(
                    Circle(coor[0], coor[1], fill=False, edgecolor='red'))

        if ld["freehand"]:
            freehand = ld["freehand"]
            for fh in freehand:
                for coor in fh:
                    x_coords, y_coords = zip(*fh)
                    self.ax.plot(
                        x_coords, y_coords, color='red')
        self.canvas.draw()

    def img_show(self, img, cmap='viridis', init=False, clear=False):
        if init:
            self.ax = self.canvas.figure.subplots()
        if clear:
            self.ax.clear()
        self.ax.imshow(img, cmap=cmap)
        self.canvas.draw()

    def erase_annotation(self, erase_dict=False):
        for patch in self.ax.patches:
            patch.remove()
        for patch in self.ax.lines:
            patch.remove()
        self.canvas.draw()

        if erase_dict:
            # del self.dd.frame_label_dict[self.dd.frame_number]
            self.dd.frame_label_dict[self.dd.frame_number] = copy.deepcopy(
                self.dd.label_dict_schema)
            print("초기화된 frame_label_dict", self.dd.frame_label_dict)

    def mp4_windowing_change(self, dd: DcmData, dx: float, dy: float):
        
        # print(type(frame)) : ndarray
        # print(frame.shape) : (720, 1280, 3)
        # print(b, g, r)
        dd.video_wl = round(dd.video_wl + dx, 2)
        dd.video_ww = round(dd.video_ww - dy, 2)
        print(dd.video_wl, dd.video_ww)
        # cv2.convertScaleAbs(frame, frame, alpha=(255.0 / dd.video_ww), beta=(dd.video_wl - dd.video_ww / 2))
        frame = self.frame_apply_windowing(dd, dd.image)
        self.func()
        # print(type(frame))
        self.img_show(frame, clear=True)

    def frame_apply_windowing(self, dd, frame):
        b, g, r = cv2.split(frame)
        r = cv2.convertScaleAbs(r, alpha=abs(1.0), beta=(dd.video_wl - dd.video_ww / 2))
        g = cv2.convertScaleAbs(g, alpha=abs(1.0), beta=(dd.video_wl - dd.video_ww / 2))
        b = cv2.convertScaleAbs(b, alpha=abs(1.0), beta=(dd.video_wl - dd.video_ww / 2))
        return cv2.merge((b, g, r))
        
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
