#!/usr/bin/env python3

import cv2

# CONSTANTS
REDLOWER = (0, 100, 100)
REDUPPER = (20, 255, 255)


cam = cv2.VideoCapture(0)

frames = 0
while True:
    
    # get frame
    frames += 1
    ret,frame = cam.read()

    # prep image
    blurred = cv2.GaussianBlur(frame, (11, 11), 0)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # make mask for red
    mask = cv2.inRange(hsv, REDLOWER, REDUPPER)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # find contours
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find center of contour
    if not contours:
        continue

    cv2.imshow('blurred', blurred)
    cv2.imshow('mask', mask)

    if cv2.waitKey(1) == 27:
        break
