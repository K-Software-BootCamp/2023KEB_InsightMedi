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
        self.label_dict_schema = {"line": [], "rectangle": [],
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
        
        if self.file_extension == "DCM" or self.file_extension == "dcm":
            self.open_dcm_file(fname)
            self.load_label_dict()
        elif self.file_extension == "mp4":
            self.open_mp4_file(fname)
    
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
    
    def save_label(self):
        for key in self.frame_label_dict:
            with open(f"{self.label_dir}/{key}.txt", 'w') as f:
                f.write(json.dumps(self.frame_label_dict[key]))
    
    def add_label(self, key, value):
        try:
            ld =  self.frame_label_dict[self.frame_number]
        except KeyError:
            self.frame_label_dict[self.frame_number]  = self.label_dict_schema.copy()
            ld =  self.frame_label_dict[self.frame_number]
        ld[key].append(value)

    def open_dcm_file(self, fname):
        self.ds = dcmread(fname[0])
        self.pixel = self.ds.pixel_array
        if len(self.pixel.shape) == 3:
            self.image = self.pixel[0]
        else:
            self.image = self.pixel

    def open_mp4_file(self, fname):
        self.frame_number = 0
        self.video_player = cv2.VideoCapture()
        self.video_player.open(fname[0])
        self.total_frame = int(self.video_player.get(cv2.CAP_PROP_FRAME_COUNT))
        
        ret, frame = self.video_player.read()
        if ret:
            self.image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)