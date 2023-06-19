#!/usr/bin/env python3

import cv2
from imutils.video import VideoStream
import imutils
import time

# read image and wait for user input
img = cv2.imread('./markers/aruco-4x4-0.png')

cv2.imshow('Image', img)
while True:
  if cv2.waitKey(500) == 27:
    break

# open video stream and wait for camera to start
print("[INFO] starting video stream...")

cap = cv2.VideoCapture(0)
#vs = VideoStream().start()
#time.sleep(2.0)

# set aruco dictionary and parameters
arucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
arucoParams = cv2.aruco.DetectorParameters_create()


# For updated API
'''
dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
parameters =  cv2.aruco.DetectorParameters()
detector = cv2.aruco.ArucoDetector(dictionary, parameters)
'''

# start video loop
while True:

  # get new webcam frame
  #frame = vs.read()
  #img = imutils.resize(frame, width=1000)
  ret, img = cap.read()

  # for updated API
  #markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(img)
  (markerCorners, markerIds, rejectedCandidates) = cv2.aruco.detectMarkers(img, arucoDict,parameters=arucoParams)

  # show corners on image if found
  if markerCorners:
    markerIds = markerIds.flatten()

    for markerCorner, markerID in zip(markerCorners, markerIds):
      # get corners
      corners = markerCorner.reshape((4, 2))
      (topLeft, topRight, bottomRight, bottomLeft) = corners

      # convert to ints
      topRight    = (int(topRight[0]),    int(topRight[1]))
      bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
      bottomLeft  = (int(bottomLeft[0]),  int(bottomLeft[1]))
      topLeft     = (int(topLeft[0]),     int(topLeft[1]))

      # draw the bounding box of the ArUCo detection
      cv2.line(img, topLeft, topRight, (0, 255, 0), 2)
      cv2.line(img, topRight, bottomRight, (0, 255, 0), 2)
      cv2.line(img, bottomRight, bottomLeft, (0, 255, 0), 2)
      cv2.line(img, bottomLeft, topLeft, (0, 255, 0), 2)

      # draw center of Aruco marker
      cX = int((topLeft[0] + bottomRight[0]) / 2.0)
      cY = int((topLeft[1] + bottomRight[1]) / 2.0)
      cv2.circle(img, (cX, cY), 4, (0, 0, 255), -1)

      # draw marker ID
      cv2.putText(img, str(markerID), (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
      print("[INFO] ArUco marker ID: {}".format(markerID))

  # show the output image
  cv2.imshow("Image", img)

  k = cv2.waitKey(1)
  if k == 27:
    break

cv2.destroyAllWindows()
cap.release()
#vs.stop()
