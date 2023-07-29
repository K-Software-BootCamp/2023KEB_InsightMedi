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
        self.frame_label_dict = {}  # {"frame_number”: {”type”: {”label id1”: {coords: [], color : “” }}, “label id2”: [coords]}

        self.label_id = 0

        self.ds = None
        self.pixel = None
        self.image = None

        self.video_player = None
        self.frame_number = 0
        self.total_frame = 0
        # self.video_wl = 255
        # self.video_ww = 255

    def open_file(self, fname, *args, **kwargs):
        self.file_path = fname[0]
        self.file_extension = fname[0].split('/')[-1].split(".")[-1]
        self.file_name = fname[0].split('/')[-1].split(".")[0]
        self.file_dir = os.path.dirname(fname[0])
        self.label_dir = self.file_dir + f"/{self.file_name}"
        self.frame_label_dict.clear()
        self.all_label = set()
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
            frame_dict = {}
            if file_name.endswith('.txt'):
                try:
                    filepath = os.path.join(self.label_dir, file_name)
                    with open(filepath, "r") as f:
                        t = json.load(f)
                        for key in t:
                            frame_dict[key] = t[key]
                        self.frame_label_dict[frame_number] = frame_dict

                except FileNotFoundError:
                    pass
    
        #print("load 된 label list:", self.all_label)
        #print("load된 frame_label_dict:",self.frame_label_dict)
            
    def save_label(self):
        for key in self.frame_label_dict:
            with open(f"{self.label_dir}/{key}.txt", 'w') as f:
                f.write(json.dumps(self.frame_label_dict[key]))
    
    # {"frame_number”: {”type”: {”label id1”: {coords: [], color : “” }}, “label id2”: [coords]}
    def add_label(self, drawing_type, label_name, coords, color="red"):
        #print("전체 frame별 label dictionary", self.frame_label_dict)
        try:
            frame_dict = self.frame_label_dict[self.frame_number]
            #print("현재 frame에 있는 label들", frame_dict)   # {"type:{”label id1”: {coords: [], color : “” }, "label id2":{coords: [], color: ""}}
        except KeyError:
            self.frame_label_dict[self.frame_number] = {}
            frame_dict =  self.frame_label_dict[self.frame_number]   # {}
            #print("새로운 frame에 label을 그렸을 때 text파일에 들어갈 정보 틀 생성")
        
        try:
            label_type_dict = frame_dict[drawing_type]
        except KeyError:
            frame_dict[drawing_type] = {}
            label_type_dict = frame_dict[drawing_type]
        
        print("추가될 label 이름:", label_name)
        # frame_label_dict에 label data 저장
        label_data_dict = {}
        label_data_dict['coords'] = coords
        label_data_dict['color'] = color

        label_type_dict[label_name] = label_data_dict
        print("labeel 그려진 이후 frame_label_dict\n", self.frame_label_dict)
        #ld[key].append(label_dict)
        #print("확인",ld)
        #print("현재 framenumber", self.frame_number)
        
    def open_dcm_file(self, fname):
        self.ds = dcmread(fname[0])
        self.pixel = self.ds.pixel_array
        self.total_frame = 1
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

    def delete_label(self, _label_name, frame = None):
        #try:
        #    if _label_name in self.all_label:
        #        self.all_label.remove(_label_name)
        #except KeyError:
        #    print("Not Member in all label")
        if frame:
            frame_number = frame
        else:
            frame_number = self.frame_number
            
        frame_dict = self.frame_label_dict[frame_number]
        #frame_dict.keys() : ”type”
        #frame_dict.values() : {”label id1”: {coords: [], color : “” }
        for label_dict in frame_dict.values():
            if _label_name in label_dict:
                u = label_dict.pop(_label_name)
                print("pop 한 data : ", u)
                break
        print(f"라벨 정보 제거 후: {self.frame_label_dict}")
    
    def modify_label_data(self, _label_name, _coor, _color):
        frame_dict = self.frame_label_dict[self.frame_number]
        for label_dict in frame_dict.values():
            if _label_name in label_dict:
                label_dict[_label_name]['coords'] = _coor
                label_dict[_label_name]['color'] = _color
                break
        print(self.frame_label_dict)

    def frame_label_check(self, frame):
        try:
            frame_dict = self.frame_label_dict[frame]
            label_list = []
            for _, label_dict in frame_dict.items():
                for label in label_dict:
                    label_list.append(label)
            
            if len(label_list) == 0:
                return False
            else:
                return label_list
        except:
            return False