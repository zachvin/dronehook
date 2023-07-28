#!/usr/bin/env python3

# Dronehook module for detecting ArUco marker in frame with Jetson Nano
# Version 0.8
# Zach Vincent (zvincent@nd.edu)
# 07-17-23

import cv2
import time
import control
import matplotlib.pyplot as plt

PWM_MODES = {
    0: control.calculate_pwm_linear,
    1: control.calculate_pwm_parabolic,
}


# set up sensor and build pipeline to import photo to file
def build_pipeline(SENSOR_ID = 0, 
                   CAP_WIDTH = 1920, 
                   CAP_HEIGHT = 1080,
                   DISP_WIDTH = 960, 
                   DISP_HEIGHT = 540,
                   FRAMERATE = 30, 
                   FLIP = 0):
    
    PIPELINE = f'nvarguscamerasrc sensor-id={SENSOR_ID} ! video/x-raw(memory:NVMM), width=(int){CAP_WIDTH}, height=(int){CAP_HEIGHT}, framerate=(fraction){FRAMERATE}/1 ! nvvidconv flip-method={FLIP} ! video/x-raw, width=(int){DISP_WIDTH}, height=(int){DISP_HEIGHT}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'

    # open video stream and wait for camera to start
    print("[INFO] starting video stream...")
    return cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)


# detect aruco marker and draw/print to console
def detect_aruco(frame,
                 detector,
                 draw=True,
                 log=True):
    
    centers = []

    # find corners and display
    marker_corners, marker_ids, rejected_candidates = detector.detectMarkers(frame)
    if marker_corners:
        marker_ids = marker_ids.flatten()

        for marker_corner, marker_id in zip(marker_corners, marker_ids):
            # get corners
            corners = marker_corner.reshape((4, 2))
            (top_left, top_right, bottom_right, bottom_left) = corners

            # convert corners to int
            top_right    = (int(top_right[0]),    int(top_right[1]))
            bottom_right = (int(bottom_right[0]), int(bottom_right[1]))
            bottom_left  = (int(bottom_left[0]),  int(bottom_left[1]))
            top_left     = (int(top_left[0]),     int(top_left[1]))

            # find center of marker
            cX = int((top_left[0] + bottom_right[0]) / 2.0)
            cY = int((top_left[1] + bottom_right[1]) / 2.0)
            centers.append((cX,cY))

            if draw:
                # draw center
                cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

                # draw bounding box
                cv2.line(frame, top_left, top_right, (0, 255, 0), 2)
                cv2.line(frame, top_right, bottom_right, (0, 255, 0), 2)
                cv2.line(frame, bottom_right, bottom_left, (0, 255, 0), 2)
                cv2.line(frame, bottom_left, top_left, (0, 255, 0), 2)

                # draw marker ID
                cv2.putText(frame, str(marker_id),
                            (top_left[0], top_left[1] - 15),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if log:
                print("[INFO] ArUco marker ID: {}".format(marker_id))

    return centers



# build aruco detector object
def build_detector(aruco_dict=cv2.aruco.DICT_4X4_250):
    # set aruco dictionary and parameters
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters =  cv2.aruco.DetectorParameters()

    return cv2.aruco.ArucoDetector(dictionary, parameters)



# calculate rough direction of camera relative to marker centers
def calculate_error(frame, centers, draw_lines=True):
    """ Calculate X/Y error as a ratio of half frame width/height
    Args:
        frame: Frame output from camera
        centers (array): Center coordinates of each detected marker
        draw_lines (bool, optional): Draw line connecting frame center to marker center
    """

    # frame length and height
    fX = frame.shape[1]
    fY = frame.shape[0]

    # frame center
    fCX = fX//2
    fCY = fY//2

    # marker center
    mCX, mCY = centers[0]

    # calculate X and Y error
    #   err > 0     plane is too far down and right (must correct up and left)
    #   err < 0     plane is too far up and left (must correct down and right)
    x_err = (fCX - mCX) / fCX
    y_err = (fCY - mCY) / fCY

    # draw line connecting frame center to marker center
    if draw_lines:
        cv2.line(frame, (fCX,fCY), (mCX,mCY), (255, 255, 0), 2)

    # write direction change
    xdirection = f'X: %{x_err:.2f}'
    ydirection = f'Y: %{y_err:.2f}'
    cv2.putText(frame, xdirection, (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)
    cv2.putText(frame, ydirection, (10, 10), cv2.FONT_HERSHEY_SIMPLEX,
                0.5, (0, 255, 0), 2)

    # return directions
    return x_err, y_err

def start_control(connection, pwm_mode = 0, display_frame = False):
    """
    Oversee main control of the plane with image recognition input.
    Args:
        connection: Ardupilot connection of Jetson to Cube
        pwm_mode (int, optional): PWM calculation mode (0: linear, 1: parabolic)
        display_frame (bool, optional): Display camera preview as code runs
    """
    err_x_total = []
    err_y_total = []

    recognition_moving_average = [0, 0, 0, 0, 0]

    cap = build_pipeline()
    detector = build_detector()

    window_name = 'PiCam'
    
    if cap.isOpened():
        num = 0

        try:
            window = cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
            while True:

                start_time = time.time()

                # get new frame
                ret, frame = cap.read()

                # detect aruco markers
                centers = detect_aruco(frame, detector)

                # calculate orientation based on position of markers in frame
                recognition_moving_average.pop(0)
                if centers:
                    recognition_moving_average.append(1)

                    if sum(recognition_moving_average) > 3:
                        err_x, err_y = calculate_error(frame, centers)
                        err_x_total.append(err_x)
                        err_y_total.append(err_y)
                        control.calculate_pwm_linear(connection, err_x, err_y)
                else:
                    recognition_moving_average.append(0)
                    print('[INFO] No marker found')

                # detect if window is still open
                if display_frame:
                    if cv2.getWindowProperty(window_name,
                                                            cv2.WND_PROP_AUTOSIZE) >= 0:
                        cv2.imshow(window_name, frame)
                    else:
                        break

                # stop if ESC or Q pressed
                k = cv2.waitKey(10) & 0xFF
                if k == 27 or k == ord('q'):
                    print('[INFO] Quitting...')
                    break

                print(f'[FPS]\t {1.0/(time.time() - start_time):.2f}')
        
        finally:
            plt.plot(err_x_total, err_y_total)
            cap.release()
            cv2.destroyAllWindows()
            plt.show()

    else:
        print('[ERROR]: Unable to open camera')
