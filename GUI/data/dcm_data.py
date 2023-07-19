from pydicom import dcmread
import os
import matplotlib
import matplotlib.pyplot as plt
import cv2
import json
import copy

matplotlib.use("Qt5Agg")

class DcmData():
    def __init__(self) -> None:
        self.file_name = None
        self.file_dir = None
        self.file_extension = None
        self.file_mode = None  #file_mode가 'dcm'이면 dcm또는 DCM파일. file_mode가 'mp4' mp4파일을 가리킵니다.

        self.label_dir = None
        self.frame_label_dict = {}
        self.label_dict_schema = {"line": [], "rectangle": [],
                           "circle": [], "freehand": []}
        
        self.ds = None
        self.pixel = None
        self.image = None

        self.video_player = None
        self.frame_number = 0
        self.total_frame = 0
        self.video_wl = 255.0
        self.video_ww = 255.0

    def open_file(self, fname, *args, **kwargs):
        self.file_extension = fname[0].split('/')[-1].split(".")[-1]
        self.file_name = fname[0].split('/')[-1].split(".")[0]
        self.file_dir = os.path.dirname(fname[0])
        self.label_dir = self.file_dir + f"/{self.file_name}"
        self.frame_label_dict.clear()
        self.image = None

        try:
            os.mkdir(self.label_dir)
        except FileExistsError:
            pass
        
        if self.file_extension == "DCM" or self.file_extension == "dcm":
            print(cv2.__version__)
            self.file_mode = 'dcm'
            self.open_dcm_file(fname)
            self.load_label_dict()
        elif self.file_extension == "mp4":
            self.file_mode = 'mp4'
            self.open_mp4_file(fname)
            self.load_label_dict()
    
    def load_label_dict(self, custom_range=None):    # text 파일로부터 현재 label dictionary를 불러옴
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
    
    def add_label(self, key, value):    #key: label_type / value: 좌표
        #print("전체 frame별 label dictionary", self.frame_label_dict)
        try:
            ld = self.frame_label_dict[self.frame_number]
        except KeyError:
            new_label_dict_schema = copy.deepcopy(self.label_dict_schema)
            self.frame_label_dict[self.frame_number] = new_label_dict_schema
            ld =  self.frame_label_dict[self.frame_number]
            print("새로운 frame에 label을 그렸을 때 text파일에 들어갈 정보 틀 생성")

        ld[key].append(value)
        print("확인",ld)
        print("현재 framenumber", self.frame_number)
        
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

    def delete_label_file(self, file_name):
        file_path = f"{self.label_dir}/{file_name}.txt"
        print("file_path:",file_path)
        
        try:
            os.remove(file_path)
            print(f"file '{file_name}' has been deleted successfully")
        except FileNotFoundError:
            print(f"file '{file_name}' not found")
        except Exception as e:
            print(f"An error occured while deleting a file '{file_name}")