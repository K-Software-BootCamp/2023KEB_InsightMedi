#%%
import pydicom
import tkinter as tk
from PIL import Image, ImageTk
import numpy as np


class Annotation:
    def __init__(self, x1, y1, x2, y2, slice_index):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.slice_index = slice_index

class DICOMViewer:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=512, height=512)
        self.canvas.pack()
        self.slider = tk.Scale(root, from_=0, to=0, orient=tk.HORIZONTAL, command=self.on_slider_change)
        self.slider.pack()
        self.load_button = tk.Button(root, text="Load DICOM", command=self.load_dicom_file)
        self.load_button.pack()
        self.annotation = None
        self.annotations = []
        self.current_slice = 0
        self.drag_start_x = None
        self.drag_start_y = None
        self.canvas.bind("<Button-1>", self.on_canvas_click)
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)

    def load_dicom_file(self):
        dicom_path = './0002.dcm'
        ds = pydicom.dcmread(dicom_path)
        self.images = ds.pixel_array.astype(np.uint8)
        self.slider.config(to=len(self.images) - 1)
        self.slider.set(0)
        self.show_image()

    def show_image(self):
        self.canvas.delete("all")
        slice_image = self.images[self.current_slice]
        img = Image.fromarray(slice_image)
        img_tk = ImageTk.PhotoImage(img)
        self.canvas.create_image(0, 0, anchor='nw', image=img_tk)
        self.canvas.image = img_tk

        for annotation in self.annotations:
            if annotation.slice_index == self.current_slice:
                x1 = annotation.x1
                y1 = annotation.y1
                x2 = annotation.x2
                y2 = annotation.y2
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="red")

    def on_slider_change(self, value):
        self.current_slice = int(value)
        self.show_image()

    def on_canvas_click(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def on_canvas_drag(self, event):
        if self.drag_start_x is not None and self.drag_start_y is not None:
            x1, y1 = self.drag_start_x, self.drag_start_y
            x2, y2 = event.x, event.y
            self.annotation = Annotation(x1, y1, x2, y2, self.current_slice)
            self.show_image()

    def save_annotation(self):
        if self.annotation is not None:
            self.annotations.append(self.annotation)
            self.annotation = None

if __name__ == "__main__":
    root = tk.Tk()
    root.title("DICOM Viewer")
    viewer = DICOMViewer(root)
    save_button = tk.Button(root, text="Save Annotation", command=viewer.save_annotation)
    save_button.pack()
    root.mainloop()

# %%
