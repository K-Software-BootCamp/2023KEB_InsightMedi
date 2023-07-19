import copy
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.backends.backend_qt5agg import FigureCanvas as FigureCanvas
from matplotlib.patches import Circle, Rectangle
from pydicom.pixel_data_handlers.util import apply_modality_lut, apply_voi_lut


class Controller():
    def __init__(self, dd, canvas) -> None:
        self.canvas = canvas
        self.dd = dd
        self.fig = canvas.figure
        self.ax = self.fig.add_subplot(111, aspect = 'auto')

        self.annotation_mode = None
        self.cid = None

        self.start = None
        self.end = None
        self.points = []
        self.is_drawing = False
        self.is_panning = False
        self.pan_Start = None
        

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
                    pass
                
            self.canvas.draw()

    def set_mpl_connect(self, *args):
        """다음순서로 args받아야 합니다. button_press_event, motion_notify_event, button_release_event"""
        cid1 = self.canvas.mpl_connect('button_press_event', args[0])
        cid2 = self.canvas.mpl_connect('motion_notify_event', args[1])
        cid3 = self.canvas.mpl_connect('button_release_event', args[2])
        self.cid = [cid1, cid2, cid3]

        cid4 = self.canvas.mpl_connect('button_press_event', self.on_pan_mouse_press)
        cid5 = self.canvas.mpl_connect('motion_notify_event', self.on_pan_mouse_move)
        cid6 = self.canvas.mpl_connect('button_release_event', self.on_pan_mouse_release)
        self.cid.extend([cid4, cid5, cid6])

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
            #del self.dd.frame_label_dict[self.dd.frame_number]
            self.dd.frame_label_dict[self.dd.frame_number] = copy.deepcopy(self.dd.label_dict_schema)
            print("초기화된 frame_label_dict", self.dd.frame_label_dict)

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

# %%
