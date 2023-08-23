<img width="187" alt="스크린샷 2023-08-23 오전 10 33 06" src="https://github.com/viroovr/InsightMedi/assets/122509996/dd9e3995-0a72-4ec6-9f62-9cab22816c7a">


# 🩻 InsightMedi
> DICOM(국제의료표준) 의료영상 라벨링 개선을 위한 라벨링툴 개발

국제의료표준인 DICOM을 공부하고 의료영상 라벨링 개선을 위한 라벨링툴을 개발하는 프로젝트입니다.

# 깃허브 링크

```
https://github.com/viroovr/InsightMedi
```

## 정보
🔥 **TEAM 살신성인** 🔥

👨🏻‍💻 팀장: 서현원(성균관) – [@Github Link](https://github.com/viroovr/)

👩🏻‍💻 팀원: 박수연(성균관) – [@Github Link](https://github.com/yeonlife/)

👩🏻‍💻 팀원: 김세은(인하) – [@Github Link](https://github.com/lavenderize/)

MIT 라이센스를 준수하며 ``LICENSE``에서 자세한 정보를 확인할 수 있습니다.



## 업데이트 내역
### ✔️ 1회차 (0712)
[dicom file open viewer 개발 계획 수립]

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


### ✔️ 3회차 (0714)
[Label drawing tool 구현]
- [x] Straight line label drawing 구현
- [x] Rectangle label drawing 구현
- [x] Circle label drawing 구현

### ✔️ 4회차 (0715)
[Windowing tool 구현]
- [x] windowing 공부 및 구현
- [x] WW, WL 값 text 화면에 보여주기
- [x] Inputdialog layout 및 0002.DCM도 windowing 조정되도록 수정하기
- [x] 줌인/아웃 하거나 다른 어노테이션 이용하고 툴이용할때 connect 유지되는거 없애기

### ✔️ 5회차 (0717)
[Open file, label list 구현]
- [x]  영상(.mp4) 파일 불러오기
- [x]  라벨 리스트 목록 보여주기
- [x]  슬라이더로 frame 조정하기

### ✔️ 6회차 (0718)
[label tool 기능 수정 및 Refacotiring]
- [x]  drawing부분 refactoring
- [x]  mp4파일 labeling
    - [x]  label list에서 button click하면 해당 frame으로 넘어가서 해당 frame에 label file이 있으면 그려주기
    - [x]  label erase 버튼 누르면 button 삭제 및 file 삭제
    - [x]  label save 버튼 누르면 button 나오게 수정하기
     
### ✔️ 7회차 (0719)
[frame 관련 기능 구현 및 UI 수정]
- [x]  windowing RGB channel에서 하는 방법 찾아보기 및 수정
- [x]  슬라이더 오른쪽에 전체 frame의 수와 현재 frame number 나타내기
- [x]  UI 색상 어둡게 변경하기

### ✔️ 8회차 (0720)
[frame 관련 기능 수정 및 UI 수정]
- [x]  frame update (slider bar / play button) 중복 호출 문제 해결
- [x]  canvas의 ax영역 deafult 색깔 설정하기
- [x]  Selector 만들기
- [x]  gui 사이드에 frame 버튼, label 버튼 생성

### ✔️ 9회차 (0721)
- [x]  selector기능에서 다른 annotation 이동 가능하게 하기
- [x]  tool status
- [x]  video status
- [x]  연속적으로 annotation 이동, drawing, windowing 구현
- [x]  각 기능에 맞게 cursor 모양 변경
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
- [x]  윈도윙 끝나면 라벨 보여주기
- [x]  기존 status bar에 있는 것들 화면으로 옮기기
    - [x]  set_window_label
    - [x]  set_tool_status_label
    - [x]  set_frame_label (slider bar 옆에)
- [x]  status bar에는 현재 파일의 경로 보여주기로 변경
- [x]  delete all 하면 버튼 다 비활성화 되는 것 수정하기

--- 

### ✔️ 팀프로젝트 1주차 (0726 - 0729)
- [x] GUI design 마무리
- [x] opencv object detection 알고리즘 관련 논문 리뷰
- [x] TrackerBoosting, TrackerMIL, TrackerMOSSE, TLD, GOTURN, CSRT, KCF, MedianFlow 샘플 테스트 진행
    - [x] CSRT 알고리즘 채택

### ✔️ 팀프로젝트 2주차 (0731 - 0805)
- [x] CSRT 알고리즘 test_gui
- [x] Bounding box drawing 기능 구현
    - [x] t누르며 바운딩박스 좌표값 얻기 → 좌표값을 프레임 dict에저장 → 프레임 업데이트
- [x] 현재 한 프레임에 여러 개의 라벨이 있을 때, 딕셔너리에 저장된 첫 번째 라벨만 object tracking 됨 → 선택된 라벨이 object tracking 될 수 있도록 수정
- [x] self.annotation 기능 구현

1. 0번 프레임에 두 라벨을 그린 모습.
![1 PNG](https://github.com/viroovr/InsightMedi/assets/122509996/141a6fab-9bbf-4600-a26a-2990b8e4d083)

2. esc클릭 또는 배경 선택 시 라벨들의 선택이 해제됨.
![2 PNG](https://github.com/viroovr/InsightMedi/assets/122509996/8d721f46-df70-4a98-91c6-272639de89f4)

3. 첫번째 라벨을 선택하고 14번 프레임까지 트랙킹하고 두번째 라벨을 선택하고 동일하게 트랙킹 한 후 14번 프레임의 모습. 선택된 라벨 각각 트랙킹이 가능함.
![3 PNG](https://github.com/viroovr/InsightMedi/assets/122509996/95ab848f-9b41-4cfe-8d23-c02b970196e4)

### ✔️ 팀프로젝트 3주차 (0807 - 0812)
- [x] multi object tracking 위해 check bbox 함수 return 형식 2차원 list로 수정
- [x] tracking 수행할 시 지연 감소를 위한 refactoring 진행
- [x] test sample DICOM file 제작
- [x] tracking 정확도 개선
    - [x] 이미지 유사도 관련 opencv API 리서치
    - [x] 이미지 유사도 계산 함수 hsv 히스토그램으로 수정
    - [x] t 한번 누르면 영상 재생되면서 object tracking 되도록 수정
    - [x] 라벨 좌표 화면 밖으로 튀는 것 감지하기

### ✔️ 팀프로젝트 4주차 (0816 - 0819)
- [x] label button 클릭했을 때 현재 frame의 label 만 지워지도록 수정
- [x] tracking 버튼 및 텍스트 박스 UI/UX 추가
- [x] 화면을 벗어나는 라벨일 경우 object tracking 중지하도록 구현
- [x] 코드 리팩토링

### ✔️ 팀프로젝트 5주차 (0821 - 0825)
- [x] 의료 비디오 영상 single/multi object tracking 시연 영상
- [x] DICOM 형식 파일 시연 영상
- [x] InsightMedi 오류 수정 및 최종 점검

## Acknowledgement

```
"본 연구는 과학기술정보통신부 및 정보통신기획평가원의 SW전문인재양성사업의 연구결과로 수행되었음"(2022-0-01127)
```
