#!/usr/bin/env python3

import numpy as np
import cv2
from imutils.video import VideoStream
import imutils
import time

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

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TermCriteria_MAX_ITER, 30, 0.001)

# prepare object points
objp = np.zeros((NUM_COLS * NUM_ROWS, 3), np.float32)
objp[:,:2] = np.mgrid[0:NUM_COLS,0:NUM_ROWS].T.reshape(-1,2)

# arrays to store object points and image points
objpoints = []
imgpoints = []

cap = cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

framenum = 0

if cap.isOpened():
    while True:
        # check if max number of images required has been reached
        if framenum > MAX_FRAMENUM:
            break

        # get image
        ret, frame = cap.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        ret, corners = cv2.findChessboardCorners(gray, (NUM_COLS,NUM_ROWS), None)

        if ret == True:

            # draw chessboard corners
            print("[INFO] Chessboard recognized")
            cv2.drawChessboardCorners(frame, (NUM_COLS, NUM_ROWS), corners, ret)

            # check if spacebar pressed and run calibration
            k = cv2.waitKey(1)
            if k == 32:
                print(f'[INFO] Running calibration on image {framenum}')
                framenum += 1

                objpoints.append(objp)

                corners2 = cv2.cornerSubPix(gray, corners, (11,11), (-1, -1), criteria)
                imgpoints.append(corners2)

        cv2.imshow('Frame', frame)

        k = cv2.waitKey(100)
        if k == 27:
            break

cv2.destroyAllWindows()

if framenum > 8:
# calibrate and save
    print('[INFO] Calibrating and saving parameters')
    ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
    np.savez('CameraCalibrationMatrices', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

    print('[INFO] Calibration and saving complete')
