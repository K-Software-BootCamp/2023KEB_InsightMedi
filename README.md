# InsightMedi 개발일지 🩻

### ✔️ 1회차 (0712)
[dicom 영상 open하는 viewer 만들기 계획 수립]

- pydicom library 이용
- dicom 영상 file open하는 기능
- 영상 위에 bounding box 그리기 기능 필요
- bounding box에 대한 정보(좌표, label, color, 두께, ...)를 text file로 저장하는 기능 <-> bounding box text file을 토대로 영상에 표현해주는 기능
- 실제 이미지와 화면상의 좌표 싱크 맞추기 필요 (image point - 이미지의 좌표, view point - 사용자 화면 상의 좌표 맞추기) -> converter 만들기! (중요)
- bounding box에 대한 pixel size 표시해주는 기능도 추가하면 좋을 듯
- 화면 크기에 맞추어 line, bounding box 늘어나도록 하기 (text file 이용하여)
- windowing level 바꾸는 기능 (WW, WL)
WW: windowing width
WL: windowing center
- 이미지 확대/축소 기능

### ✔️ 2회차 (0713)
[GUI 설계하기]
https://jamboard.google.com/d/1iVxu9bzPdAtv3mv8FSZsVpwXUnWIn10biJ0JXpwbdPU/viewer?f=0
- Elements of any VR:
    - Can be set as empty by using **`None`**
    - Can have their values set using their *set using* or *stored as* type from the table below
- Non-**SQ** element values:
    - Can also be set using a **`[list](https://docs.python.org/3/library/stdtypes.html#list)`** of their *set using* type - for [Value Multiplicity](http://dicom.nema.org/medical/dicom/current/output/chtml/part05/sect_6.4.html) (VM) > 1, the value will be stored as a **`[MultiValue](https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.multival.MultiValue.html#pydicom.multival.MultiValue)`** of their *stored as* type
    - However, according to the DICOM Standard, elements with VR **LT**, **OB**, **OD**, **OF**, **OL**, **OW**, **ST**, **UN**, **UR** and **UT** should never have a VM greater than 1.
- **SQ** element values should be set using a **`[list](https://docs.python.org/3/library/stdtypes.html#list)`** of zero or more **`[Dataset](https://pydicom.github.io/pydicom/stable/reference/generated/pydicom.dataset.Dataset.html#pydicom.dataset.Dataset)`** instances.

### ✔️ 3회차 (0714)
[Label 그리기 구현]
- 사각형 label 그리기 구현
- 직선 label 그리기 구현
- 원 label 그리기 구현

### ✔️ 4회차 (0715)
- [x] windowing 공부 및 구현
- [x] WW, WL 값 text 화면에 보여주기
- [x] Inputdialog layout 및 0002.DCM도 windowing 조정되도록 수정하기
- [x] 줌인/아웃 하거나 다른 어노테이션 이용하고 툴이용할때 connect 유지되는거 없애기

### ✔️ 5회차 (0717)
- [x]  영상(.mp4) 파일 불러오기
- [x]  라벨 리스트 목록 보여주기
- [x]  슬라이더로 frame 조정하기

### ✔️ 6회차 (0718)
- [x]  drawing부분 refactoring
- [x]  mp4파일 labeling
    - [x]  label list에서 button click하면 해당 frame으로 넘어가서 해당 frame에 label file이 있으면 그려주기
    - [x]  label erase 버튼 누르면 button 삭제 및 file 삭제
    - [x]  label save 버튼 누르면 button 나오게 수정하기
     
### ✔️ 7회차 (0719)
- [x]  windowing RGB channel에서 하는 방법 찾아보기 및 수정
- [x]  슬라이더 오른쪽에 전체 frame의 수와 현재 frame number 나타내기
- [x]  UI 색상 어둡게 변경하기

### ✔️ 8회차 (0720)
- [x]  frame update (slider bar / play button) 중복 호출 문제 해결
- [x]  canvas의 ax영역 deafult 색깔 설정하기
- [x]  Selector 만들기
- [x]  gui 사이드에 프레임 버튼, 라벨 버튼 보여주기

### ✔️ 9회차 (0721)
- [x]  selector기능에서 다른 어노테이션들도 이동가능하게 하기
- [x]  tool status 보여주기 
- [x]  video status 보여주기 
- [x]  연속적으로 라벨이동, 드로윙, 윈도윙 보여주기
- [x]  각 기능에 맞게 커서 모양 변경
- [x]  label dictionary 수정하기 ex) {”frame_number” : {“label id” : {label_dict_schema}, {”label id2” : {label_dict_schema}}

### ✔️ 10회차 (0722)
- [x]  라벨 버튼 10개 with go button (현재 frame button) 나타나게 하기
- [x]  label button 클릭 시 label button과 go button에 변화 주기(글꼴 색깔, 굵기 변화)
- [x]  label button 클릭 시 rectangle label 그리기 모드로 전환되기
- [x]  go button 클릭 시 함수 구현하기
- [x]  canvas ax 축 안 보이게 하기 
- [x]  단일 객체 드래그 시 dict에서도 좌표값 옮기기 
- [x]  단일 객체 지우개 기능 사용 하면 dict에서도 지우기 (all_label set 에서도 지우기) (frame_label_dict, 화면에서 삭제, 라벨 버튼지우기)

### ✔️ 11회차 (0724)
- [x]  라벨 저장 방식 수정하기: draw_annotation과 add_label 함수에서 label name assign 되는 방식 수정하기
draw_annotation에서 아예 label name을 함수의 parameter로 받도록
- [x]  dcm_data.py 파일에 frame을 입력하였을 때, self.dd.frame_label_dict에서 해당 frame에 있는 label들을 확인할 수 있는 함수 frame_label_check(self, frame) 함수 만들기 return은 label_list(해당 frame의 라벨들이 있는 리스트)
사용 예시 ex) frame_label_check(self.dd.frame_number)
- [x]  label button 클릭하면 기존 label은 삭제되고 새로운 label을 그릴 수 있도록 tool status를 바꿔주고 하나의 label을 그리고 나면 selector status로 변경될 수 있도록 label_button_clicked 함수 수정하기 + label 한 개 그리고 drawing disconnect
- [x]  다른 파일 열면 활성화된 button들 다시 초기화 하기
- [x]  erase 하면 label 버튼 비활성화 및 라벨 삭제하기
- [x]  전체 어노테이션 지우기 기능 수정
- [x]  라벨 클릭시 해당 프레임 이동후 두께 강조 
- [x]  어노테이션 드로윙 마치면 다른 어노테이션 두께 원상태
- [x]  랜덤 색상값으로 그리기 추가 
- [x]  modift label data 함수 수정하기

### ✔️ 12회차 (0725)
- [x]  **code refactoring**
    - [x]  viewer_gui refactoring
    - [x]  control
- [x]  윈도윙 하면 라벨 지워지는 거 - 차선책 윈도윙 끝나면 보여주기.
- [x]  기존 status bar에 있는 것들 화면으로 옮기기
    - [x]  set_window_label
    - [x]  set_tool_status_label
    - [x]  set_frame_label (slider bar 옆에)
- [x]  status bar에는 현재 파일의 경로 보여주기로 변경
- [x]  delete all 하면 버튼 다 비활성화 되는 것 수정하기

["본 연구는 과학기술정보통신부 및 정보통신기획평가원의 SW전문인재양성사업의 연구결과로 수행되었음"(2022-0-01127) ]
