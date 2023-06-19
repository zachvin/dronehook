#!/usr/bin/env python3

import cv2

MAX_FRAMENUM = 14
NUM_COLS =  4
NUM_ROWS = 4

SENSOR_ID   = 0
CAP_WIDTH   = 1920
CAP_HEIGHT  = 1080
DISP_WIDTH  = 960
DISP_HEIGHT = 540
FRAMERATE   = 30
FLIP        = 0

PIPELINE = f'nvarguscamerasrc sensor-id={SENSOR_ID} ! video/x-raw(memory:NVMM), width=(int){CAP_WIDTH}, height=(int){CAP_HEIGHT}, framerate=(fraction){FRAMERATE}/1 ! nvvidconv flip-method={FLIP} ! video/x-raw, width=(int){DISP_WIDTH}, height=(int){DISP_HEIGHT}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

window_name = 'Frame'
if cap.isOpened():
    num = 0

    try:
        window = cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        while True:
            ret, frame = cap.read()
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_AUTOSIZE) >= 0:
                cv2.imshow(window_name, frame)
            else:
                break

            k = cv2.waitKey(10) & 0xFF
            if ret:
                if k == 32:
                    print('[INFO] Saving image...')
                    if cv2.imwrite(f'./img/calib-{num:02}.jpg', frame):
                        print(f'\tSuccessfully saved at /img/calib-{num:02}.jpg')
                        num += 1
                

            if k == 27 or k == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

else:
    print('[ERROR]: Unable to open camera')
