import cv2 as cv
import numpy as np
import json

NUM_COLS =  6
NUM_ROWS = 7

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TermCriteria_MAX_ITER, 30, 0.001)

# prepare object points
objp = np.zeros((NUM_COLS * NUM_ROWS, 3), np.float32)
objp[:,:2] = np.mgrid[0:NUM_COLS,0:NUM_ROWS].T.reshape(-1,2)

# arrays to store object points and image points
objpoints = []
imgpoints = []

good_images = []

img = cv.imread(f'./img/calib-0.jpg')
gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

for i in range(13):
    fname = f'./img/calib-{i:02}.jpg'
    img = cv.imread(fname)
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)

    # find chessboard corners
    ret, corners = cv.findChessboardCorners(gray, (NUM_COLS, NUM_ROWS), None)

    # refine points and add (should run on all photos, i.e. all photos should have successful recognition)
    if ret:
        good_images.append(fname)
        print(f'[INFO] image {fname} detected')
        objpoints.append(objp)

        subcorners = cv.cornerSubPix(gray, corners, (11,11), (-1,-1), criteria)
        imgpoints.append(subcorners)

        # draw and display corners
        cv.drawChessboardCorners(img, (NUM_COLS, NUM_ROWS), subcorners, ret)
        cv.imshow('img', img)
        k = cv.waitKey(500)
        if k == 27:
            break
    else:
        print(f'[ERROR] image {fname} not detected')

cv.destroyAllWindows()

# calibrate
ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

# save parameters
np.savez('distortionparams', mtx=mtx, dist=dist, rvecs=rvecs, tvecs=tvecs)

print('[INFO] Parameters saved')
