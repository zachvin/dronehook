#!/usr/bin/env python3

from pymavlink import mavutil
import cv2
import time

# start connection
connection = mavutil.mavlink_connection('/dev/ttyACM0')

def set_rc_channel_pwm(channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 18:
        print("Channel does not exist.")
        return

    # Mavlink 2 supports up to 18 channels:
    # https://mavlink.io/en/messages/common.html#RC_CHANNELS_OVERRIDE
    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    connection.mav.rc_channels_override_send(
        connection.target_system,                # target_system
        connection.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.
    
# wait for first heartbeat. sets system and component ID of remote system for the link
connection.wait_heartbeat()
print(f'Heartbeat from system (system {connection.target_system} component {connection.target_component})')

#
# set up sensor and build pipeline to import frame to file
#
def build_pipeline(SENSOR_ID = 0, CAP_WIDTH = 1920, CAP_HEIGHT = 1080, DISP_WIDTH = 960, DISP_HEIGHT = 540, FRAMERATE = 30, FLIP = 0):
    PIPELINE = f'nvarguscamerasrc sensor-id={SENSOR_ID} ! video/x-raw(memory:NVMM), width=(int){CAP_WIDTH}, height=(int){CAP_HEIGHT}, framerate=(fraction){FRAMERATE}/1 ! nvvidconv flip-method={FLIP} ! video/x-raw, width=(int){DISP_WIDTH}, height=(int){DISP_HEIGHT}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink'

    # open video stream and wait for camera to start
    print("[INFO] starting video stream...")
    return cv2.VideoCapture(PIPELINE, cv2.CAP_GSTREAMER)

#
# detect aruco marker and draw/print to console
#
def detect_aruco(frame, draw=True, log=True):
    centers = []

    # find corners and display
    markerCorners, markerIds, rejectedCandidates = detector.detectMarkers(frame)
    if markerCorners:
        markerIds = markerIds.flatten()

        for markerCorner, markerID in zip(markerCorners, markerIds):
            # get corners
            corners = markerCorner.reshape((4, 2))
            (topLeft, topRight, bottomRight, bottomLeft) = corners

            # convert corners to int
            topRight    = (int(topRight[0]),    int(topRight[1]))
            bottomRight = (int(bottomRight[0]), int(bottomRight[1]))
            bottomLeft  = (int(bottomLeft[0]),  int(bottomLeft[1]))
            topLeft     = (int(topLeft[0]),     int(topLeft[1]))

            # find center of marker
            cX = int((topLeft[0] + bottomRight[0]) / 2.0)
            cY = int((topLeft[1] + bottomRight[1]) / 2.0)
            centers.append((cX,cY))

            if draw:
                # draw center
                cv2.circle(frame, (cX, cY), 4, (0, 0, 255), -1)

                # draw bounding box
                cv2.line(frame, topLeft, topRight, (0, 255, 0), 2)
                cv2.line(frame, topRight, bottomRight, (0, 255, 0), 2)
                cv2.line(frame, bottomRight, bottomLeft, (0, 255, 0), 2)
                cv2.line(frame, bottomLeft, topLeft, (0, 255, 0), 2)

                # draw marker ID
                cv2.putText(frame, str(markerID), (topLeft[0], topLeft[1] - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            if log:
                print("[INFO] ArUco marker ID: {}".format(markerID))

    return centers


#
# build aruco detector object
#
def build_detector(aruco_dict=cv2.aruco.DICT_4X4_250):
    # set aruco dictionary and parameters
    dictionary = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250)
    parameters =  cv2.aruco.DetectorParameters()

    return cv2.aruco.ArucoDetector(dictionary, parameters)


#
# calculate rough direction of camera relative to marker centers
#
def calculate_orientation(frame, centers, draw_lines=True):

    # frame length and height
    fX = frame.shape[1]
    fY = frame.shape[0]

    # frame center
    fCX = fX//2
    fCY = fY//2

    # marker center
    mCX, mCY = centers[0]

    # determine req'd direction to move to center aruco marker for X
    if mCX > fCX:
        xdirection = 'left'
    elif mCX < fCX:
        xdirection = 'right'
    else:
        xdirection = 'center'

    # determine req'd direction to move to center aruco marker for Y
    if mCY > fCY:
        ydirection = 'up'
    elif mCY < fCY:
        ydirection = 'down'
    else:
        ydirection = 'center'

    # draw direction lines
    if draw_lines:
        cv2.line(frame, (fCX,fCY), (mCX,mCY), (255, 255, 0), 2)

    # write direction change
    xdirection = f'X: {xdirection}'
    ydirection = f'Y: {ydirection}'
    cv2.putText(frame, xdirection, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    cv2.putText(frame, ydirection, (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # return directions
    return xdirection, ydirection

    

#cap = build_pipeline(DISP_WIDTH=1920, DISP_HEIGHT=1080)
cap = build_pipeline()
detector = build_detector()

window_name = 'Frame'
if cap.isOpened():
    num = 0

    try:
        window = cv2.namedWindow(window_name, cv2.WINDOW_AUTOSIZE)
        while True:
            # get new frame
            ret, frame = cap.read()

            # detect aruco markers
            centers = detect_aruco(frame)

            # calculate orientation based on position of markers in frame
            if centers:
                xdir, ydir = calculate_orientation(frame, centers)
                if xdir == 'left':
                    set_rc_channel_pwm(1, 1200)
                else:
                    set_rc_channel_pwm(1, 1800)
            else:
                print('[INFO] No marker found')

            # detect if window was closed
            if cv2.getWindowProperty(window_name, cv2.WND_PROP_AUTOSIZE) >= 0:
                cv2.imshow(window_name, frame)
            else:
                break

            # close window if ESC or Q pressed
            k = cv2.waitKey(10) & 0xFF
            if k == 27 or k == ord('q'):
                break
    
    finally:
        cap.release()
        cv2.destroyAllWindows()

else:
    print('[ERROR]: Unable to open camera')
