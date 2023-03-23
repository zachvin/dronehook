#!/usr/bin/env python3

import cv2
import numpy as np

def nothing(x):
    pass

def get_hsv(event, x, y, flags, param):
    global ix, iy, show_hsv

    if event == cv2.EVENT_LBUTTONDOWN:
       ix,iy,show_hsv = x,y,True 
        

REDLOWER = (0, 100, 100)
REDUPPER = (20, 255, 255)
h = 0
s = 100
v = 100

ix,iy,show_hsv = 0, 0, False
tar_h, tar_s, tar_v = 0, 0, 0

cam = cv2.VideoCapture(0)

cv2.namedWindow('mask')
cv2.namedWindow('blurred')

cv2.setMouseCallback('blurred', get_hsv)

cv2.createTrackbar('H', 'mask', 0, 20, nothing)
cv2.createTrackbar('S (amt. of white)', 'mask', 0, 100, nothing)
cv2.createTrackbar('V (amt. of black)', 'mask', 0, 100, nothing)

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
    mask = cv2.inRange(hsv, (h,s,v), REDUPPER)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    # get HSV at mouse location on click
    if show_hsv:
        tar_h = blurred.item(ix,iy,0)
        tar_s = blurred.item(ix,iy,1)
        tar_v = blurred.item(ix,iy,2)
        show_hsv = False

    hsv_str = f'H {tar_h}\nS {tar_s}\nV {tar_v}'
    cv2.putText(blurred, hsv_str, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0))

    # show image
    cv2.imshow('blurred', blurred)
    cv2.imshow('mask', mask)

    # HSV sliders
    h = cv2.getTrackbarPos('H', 'mask')
    s = cv2.getTrackbarPos('S (amt. of white)', 'mask')
    v = cv2.getTrackbarPos('V (amt. of black)', 'mask')

    # find contours
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # find center of contour
    if not contours:
        continue

    if cv2.waitKey(1) == 27:
        break
