import cv2
print(cv2.__version__)
tracker = cv2.TrackerKCF_create()
#tracker = cv2.TrackerCSRT_create()

video = cv2.VideoCapture('sample\street')   # 영상 불러오기

ok, frame = video.read()   # ok: opencv에서 영상을 읽을 수 있는 지 / frame: 영상의 frame

bbox = cv2.selectROI(frame)   # 첫 번쨰 frame의 정보만 저장하고 있음
#print(bbox)   # bounding box 위치

ok = tracker.init(frame, bbox)    # frame의 bounding box tracking 시작
#print(ok)

while True:
    ok, frame = video.read()

    if not ok:
        break

    # frame update하기 (bbox에 있는 frame은 첫 번째 frame으로 고정되어 있음
    ok, bbox = tracker.update(frame)
    #print(bbox)
    #print(ok)

    if ok:
        (x, y, w, h) = [int(v) for v in bbox]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2, 1)   # 두께: 2, 윤곽선: 1
    else:
        cv2.putText(frame, 'Error', (100,80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255))

    cv2.imshow("Tracking", frame)
    if cv2.waitKey(1) & 0XFF == 27:   # ESC 누르면 창 닫힘
        break