import numpy as np
import cv2 as cv
import time

MAX_FRAMENUM = 14

cap = cv.VideoCapture(0)

framenum = 0
while True:
    ret, frame = cap.read()

    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

    ret, corners = cv.findChessboardCorners(gray, (7,6), None)


    if ret == True:
        print("IMAGE TAKEN")
        print(cv.imwrite(f'./calib/calib_image_{framenum}.jpg', frame))
        cv.drawChessboardCorners(frame, (7,6), corners, ret)

        framenum += 1

        if framenum > MAX_FRAMENUM:
            break

        time.sleep(1)

    cv.imshow('Frame', frame)

    k = cv.waitKey(100)
    if k == 27:
        break


cv.destroyAllWindows()