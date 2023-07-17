from pydicom import dcmread
import os
import matplotlib.pyplot as plt
import cv2
import json

class DcmData():
    def __init__(self) -> None:
        self.file_name = None
        self.file_dir = None
        self.file_extension = None
        
        self.label_dir = None
        self.frame_label_dict = {}
        self.label_dict = {"line": [], "rectangle": [],
                           "circle": [], "freehand": []}
        
        
        self.ds = None
        self.pixel = None
        self.image = None
        self.frame_number = 0
        self.total_frame = 0
    
    def open_file(self, fname, *args, **kwargs):
        self.file_extension = fname[0].split('/')[-1].split(".")[-1]
        self.file_name = fname[0].split(sep='/')[-1].split(sep=".")[0]
        self.file_dir = os.path.dirname(fname[0])
        self.label_dir = self.file_dir + f"/{self.file_name}" 
        try:
            os.mkdir(self.label_dir)
        except FileExistsError:
            pass

        self.open_dcm_file(fname)
        self.load_label_dict()
    
    def load_label_dict(self, custom_range=None):
        for file_name in sorted(os.listdir(self.label_dir)):
            print(file_name)
            frame_number = int(file_name.split(".")[0])
            label_dict = {}
            if file_name.endswith('.txt'):
                try:
                    filepath = os.path.join(self.label_dir, file_name)
                    with open(filepath, "r") as f:
                        t = json.load(f)
                        for key in t:
                            label_dict[key] = t[key]
                        self.frame_label_dict[frame_number] = label_dict
                except FileNotFoundError:
                    pass
        
    def open_dcm_file(self, fname):
        self.ds = dcmread(fname[0])
        self.pixel = self.ds.pixel_array
        if len(self.pixel.shape) == 3:
            self.image = self.pixel[0]
        else:
            self.image = self.pixel
            # ax.imshow(pixel, cmap=plt.cm.gray)
    
    def open_mp4_file(self, fname, canvas, ax):
        self.video_player = cv2.VideoCapture()
        self.video_player.open(fname[0])
        self.total_frame = int(self.video_player.get(cv2.CAP_PROP_FRAME_COUNT))
        # self.timer = QTimer()
        print(self.total_frame)
        self.slider.setMaximum(int(self.video_player.get(cv2.CAP_PROP_FRAME_COUNT)) - 1)
        self.slider.valueChanged.connect(self.sliderValueChanged)
        self.play_button.clicked.connect(self.playButtonClicked)

        # timer start
        if not self.timer:
            self.timer = self.canvas.new_timer(interval = 33)    #30FPS
            self.timer.add_callback(self.updateFrame)
            self.timer.start()