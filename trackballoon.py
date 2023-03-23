#!/usr/bin/env python3

import cv2

def nothing(x):
    pass

REDLOWER = (0, 100, 100)
REDUPPER = (20, 255, 255)
h = 20
s = 255
v = 255

cam = cv2.VideoCapture(0)

cv2.namedWindow('mask')

cv2.createTrackbar('H', 'mask', 0, 50, nothing)
cv2.createTrackbar('S (amt. of white)', 'mask', 100, 255, nothing)
cv2.createTrackbar('V (amt. of black)', 'mask', 100, 255, nothing)

frames = 0
while True:
    
    # get frame
    frames += 1
    ret,frame = cam.read()

    if frame is None:
        continue

    # prep image
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)


    # make mask for red
    mask = cv2.inRange(hsv, REDLOWER, (h,s,v))
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # show image
    cv2.imshow('blurred', blurred)
    cv2.imshow('mask', mask)

    # HSV sliders
    h = cv2.getTrackbarPos('H', 'mask')
    s = cv2.getTrackbarPos('S (red to white)', 'mask')
    v = cv2.getTrackbarPos('V (red to black)', 'mask')

    # find contours
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find center of contour
    if not contours:
        continue


    if cv2.waitKey(1) == 27:
        break
