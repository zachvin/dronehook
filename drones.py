from collections import deque
from imutils.video import VideoStream
import numpy as np
import argparse
import cv2
import imutils
import time
from dronekit import connect, VehicleMode, LocationGlobalRelative
from pymavlink import mavutil
import time
from math import cos, sin, radians

parser = argparse.ArgumentParser()
parser.add_argument('--connect', default='udpin:127.0.0.1:14551')
args = parser.parse_args()


# Connect to the Vehicle
#print( 'Connecting to vehicle on: %s' % args.connect)
#vehicle = connect(args.connect, baud=57600, wait_ready=True)

# Function to arm and then takeoff to a user specified altitude


def waypoint(lat, lon, alt):
    point1 = LocationGlobalRelative(lat, lon, alt)
    vehicle.simple_goto(point1)
    while(abs((vehicle.location.global_relative_frame.lon - lon)) > 0.1 or abs((vehicle.location.global_relative_frame.lat - lat)) > 0.1 or abs((vehicle.location.global_relative_frame.alt - alt) > 100)):
        time.sleep(1)

def arm_and_takeoff(aTargetAltitude):
  print("Basic pre-arm checks")
  # Don't let the user try to arm until autopilot is ready
  while not vehicle.is_armable:
    print(" Waiting for vehicle to initialise...")
    time.sleep(1)
  print("Arming motors")
  # Copter should arm in GUIDED mode
  vehicle.mode    = VehicleMode("GUIDED")
  vehicle.armed   = True
  while not vehicle.armed:
    print(" Waiting for arming...")
    time.sleep(1)
  vehicle.mode = VehicleMode("TAKEOFF")
  print("Taking off!")
  vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude
  # Check that vehicle has reached takeoff altitude
  while True:
    print(" Altitude: ", vehicle.location.global_relative_frame.alt) 
    #Break and return from function just below target altitude.        
    if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
      print("Reached target altitude")
      break
    time.sleep(1)

def get_balloon_gps():
         """
         Obtaining the GPS coordinates from the PIC32 via UART
         """
         dic = {}
         flag = 0;
         with serial.Serial('/dev/ttyS3', 9600, timeout=1) as UART3: #Serial Port 3 on raspi4 (should be pins 4 and 5 but check)
             while  (flag == 0):
                 line = UART3.readline()   # read a '\n' terminated line
                 if "GNGGA" in line:
                     flag = 1;
                     values = line.split(",");
         dic["latitude"] = float(value[2])
         dic["longitude"] = float(value[4])
         dic["altitude"] = float(value[9])
         return dic


def CV_Pic():
    #Output list of velocity vectors based on relative positioning in the frame
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
            print(center)
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
#    if key == ord("q"):
#        break
    grab = grab_f_e - grab_f_s
    proc = proc_f_e - proc_f_s
#	print("Grabbing: %f s, Processing: %f s" % (grab, proc))
    end = time.time()
    if frames % 100 == 0:
        estimated_fps = frames / (end - start)
#		print("Estimated FPS: %f" % estimated_fps)
    return center


def Parse_CV(center):
#Check this, probably wont work tbh
#Velocity_x and velocity_y are parallel to the North and East directions (not to the front and side of the vehicle). The velocity_z component is perpendicular to the plane of velocity_x and velocity_y, with a positive value towards the ground
    x = center[0] - 2048
    y = 1588 - center[1]
    xmax = 2048
    ymax = 1588
    #gonna need to include pi.math or something
    # python expects to intake radians
    theta = radians(vehicle.heading)
    vx = ((7-7*(x/xmax)) * (cos(theta) - sin(theta)))
    vy = 7*((x/xmax) * (sin(theta) + cos(theta)))
    vz = (y/ymax) * -3.5
    
    return([vx, vy, vz]) #Just took the ratios of the two



def send_ned_velocity(velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors and
    for the specified duration.

    This uses the SET_POSITION_TARGET_LOCAL_NED command with a type mask enabling only 
    velocity components 
    (http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_local_ned).
    
    Note that from AC3.3 the message should be re-sent every second (after about 3 seconds
    with no message the velocity will drop back to zero). In AC3.2.1 and earlier the specified
    velocity persists until it is canceled. The code below should work on either version 
    (sending the message multiple times does not cause problems).
    
    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
    """
    msg = vehicle.message_factory.set_position_target_local_ned_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_LOCAL_NED, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, 0, 0, # x, y, z positions (not used)
        velocity_x, velocity_y, velocity_z, # x, y, z velocity in m/s
        0, 0, 0, # x, y, z acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 

    # send command to vehicle on 1 Hz cycle
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)

def send_global_velocity(velocity_x, velocity_y, velocity_z, duration):
    """
    Move vehicle in direction based on specified velocity vectors.
    This uses the SET_POSITION_TARGET_GLOBAL_INT command with type mask enabling only 
    velocity components 
    (http://dev.ardupilot.com/wiki/copter-commands-in-guided-mode/#set_position_target_global_int).
    
    Note that from AC3.3 the message should be re-sent every second (after about 3 seconds
    with no message the velocity will drop back to zero). In AC3.2.1 and earlier the specified
    velocity persists until it is canceled. The code below should work on either version 
    (sending the message multiple times does not cause problems).
    
    See the above link for information on the type_mask (0=enable, 1=ignore). 
    At time of writing, acceleration and yaw bits are ignored.
    """
    msg = vehicle.message_factory.set_position_target_global_int_encode(
        0,       # time_boot_ms (not used)
        0, 0,    # target system, target component
        mavutil.mavlink.MAV_FRAME_GLOBAL_RELATIVE_ALT_INT, # frame
        0b0000111111000111, # type_mask (only speeds enabled)
        0, # lat_int - X Position in WGS84 frame in 1e7 * meters
        0, # lon_int - Y Position in WGS84 frame in 1e7 * meters
        0, # alt - Altitude in meters in AMSL altitude(not WGS84 if absolute or relative)
        # altitude above terrain if GLOBAL_TERRAIN_ALT_INT
        velocity_x, # X velocity in NED frame in m/s
        velocity_y, # Y velocity in NED frame in m/s
        velocity_z, # Z velocity in NED frame in m/s
        0, 0, 0, # afx, afy, afz acceleration (not supported yet, ignored in GCS_Mavlink)
        0, 0)    # yaw, yaw_rate (not supported yet, ignored in GCS_Mavlink) 

    # send command to vehicle on 1 Hz cycle
    for x in range(0,duration):
        vehicle.send_mavlink(msg)
        time.sleep(1)    


if __name__ == "__main__":

    #Initialize Code
    parser = argparse.ArgumentParser()
    parser.add_argument('--connect', default='udpin:127.0.0.1:14551') #Make default equal to serial port 1 /ttyAMA0 or Serial0
    args = parser.parse_args()
    # Connect to the Vehicle
    print( 'Connecting to vehicle on: %s' % args.connect)
    vehicle = connect(args.connect, baud=57600, wait_ready=True)

    # Initialize the takeoff sequence to 40m
    arm_and_takeoff(40) #Or whatever the altitude of the balloon is
    print("Take off complete")
#    while(1):
#        new = Parse_CV((2048, 1588))
#        send_ned_velocity(10, 10, -20, 1)
#        print(vehicle.location.global_relative_frame.alt)


    # Hover for 10 seconds
    time.sleep(5)

    #Fetch initial GPS Coordinates and set straight line waypoint
    vehicle.mode = VehicleMode("GUIDED")
#    coords = get_balloon_gps()  #See above
    waypoint(-35, 140.21, vehicle.location.global_relative_frame.alt)
    #waypoint(coords["latitude"], coords["longitude"], coords["altitude"]) #This is a placeholder do coords["coordinate"]
    #Here turn on CV
    time.sleep(3)

    #Use CV data to create velocity vector to edit direction to hit balloon
    #While data being received, (Probably something like not receiving 0s
    """redLower = (0, 100, 100)
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


    while (CV_Pic == None):
            pass


    while (CV_Pic):
        Vel = CV_Parse()
        send_ned_velocity(Vel[0], Vel[1], Vel[2])
    """


    #Land UAV
    print("Now let's land")
    vehicle.mode = VehicleMode('RTL')
    while(1):
        pass
        # Close vehicle object
    


    vehicle.close()



