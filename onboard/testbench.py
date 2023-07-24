#!/usr/bin/env python3

# Test bench code for Dronehook
# Version 1.0
# Zach Vincent (zvincent@nd.edu)
# 07-17-23

from pymavlink import mavutil
import time
import aruco

# START CONNECTION
connection = mavutil.mavlink_connection('/dev/ttyACM0')

# WAIT FOR HEARTBEAT
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (connection.target_system, connection.target_component))

# START ARUCO CONTROL LOOP
aruco.start_control()


# CLEAN UP
print('[INFO] Ending master control')