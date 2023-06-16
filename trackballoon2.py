import cv2
import numpy as np

# CONSTANTS
RED       = np.uint8([[[255,0,0]]])
RED_HSV   = cv2.cvtColor(RED, cv2.COLOR_BGR2HSV)
RED_UPPER = np.array([0, 100, 100])
RED_LOWER = np.array([20, 255, 255])

# start up camera
cap = cv2.videoCapture(0)

while True:
    
    # convert image to HSV
    ret,frame = cap.read()
    frame_hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # make red mask with HSV range
    mask = cv2.inRange(frame_hsv, RED_LOWER, RED_UPPER)

    # compute final image and show all images
    res = cv2.bitwise_and(frame, frame, mask=mask)

    cv2.imshow('frame', frame)
    cv2.imshow('mask', mask)
    cv2.imshow('res', res)

    k = cv2.waitKey(1)
    if k == 27:
        break