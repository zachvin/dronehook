from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-b", "--buffer", type=int, default=64, help="max buffer size")
args = vars(ap.parse_args())

# define red balloon in the HSV & initialize list of tracked points
redLower = (0, 100, 100)
redUpper = (20, 255, 255)
pts = deque(maxlen=args["buffer"])

# start video stream
vs = VideoStream(src=0).start()

# allow the camera or video file to warm up
time.sleep(2.0)

# frame count 
frames = 0

# start time 
start = time.time()

while True:
	frames += 1
	grab_f_s = time.time()
	# grab the current frame
	frame = vs.read()
	grab_f_e = time.time()

	proc_f_s = time.time()
	# resize the frame, blur it, and convert it to the HSV color space
	frame = imutils.resize(frame, width=400)
	blurred = cv2.GaussianBlur(frame, (11, 11), 0)
	hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)

	# construct a mask for the color "red" & prune to remove inconsistencies
	mask = cv2.inRange(hsv, redLower, redUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
	cnts = imutils.grab_contours(cnts)
	center = None

	# only proceed if at least one contour was found
	if len(cnts) > 0:
		# find the largest contour in the mask, then use it to compute the minimum enclosing circle and centroid
                c = max(cnts, key=cv2.contourArea)
                ((x, y), radius) = cv2.minEnclosingCircle(c)
                M = cv2.moments(c)
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                # only proceed if the radius meets a minimum size
                if radius > 10:
			# draw the circle and centroid on the frame,
			# then update the list of tracked points
                        print(center.x)
                        cv2.circle(frame, (int(x), int(y)), int(radius),(0, 255, 255), 2)
                        cv2.circle(frame, center, 5, (0, 0, 255), -1)
	
	proc_f_e = time.time()

	# update the points queue
	pts.appendleft(center)
	
	# loop over the set of tracked points
	for i in range(1, len(pts)):
		# if either of the tracked points are None, ignore
		# them
		if pts[i - 1] is None or pts[i] is None:
			continue
		# otherwise, compute the thickness of the line and
		# draw the connecting lines
		thickness = int(np.sqrt(args["buffer"] / float(i + 1)) * 2.5)
		cv2.line(frame, pts[i - 1], pts[i], (0, 0, 255), thickness)
		
	# show the frame to our screen
	cv2.imshow("Frame", frame)
	key = cv2.waitKey(1) & 0xFF	
	
	# if the 'q' key is pressed, stop the loop
	if key == ord("q"):
		break

	grab = grab_f_e - grab_f_s
	proc = proc_f_e - proc_f_s
	#print("Grabbing: %f s, Processing: %f s" % (grab, proc))

	end = time.time()
	if frames % 100 == 0:
		estimated_fps = frames / (end - start)
	#	print("Estimated FPS: %f" % estimated_fps)

# close all windows
cv2.destroyAllWindows()

# stop the camera video stream
vs.stop()
