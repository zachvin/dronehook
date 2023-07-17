#!/usr/bin/env python3

# Master control code for Dronehook
# Version 0.2
# Zach Vincent (zvincent@nd.edu)
# 07-17-23

from pymavlink import mavutil
import time
import aruco

# START CONNECTION
connection = mavutil.mavlink_connection('udpin:localhost:14551')

# WAIT FOR HEARTBEAT
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (connection.target_system, connection.target_component))


# ARM
connection.mav.command_long_send(connection.target_system,
                                 connection.target_component, 
                                 mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                 0,
                                 1, 0, 0, 0, 0, 0, 0)

msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)

# TAKEOFF
print('[INFO] TAKING OFF')
connection.mav.command_long_send(connection.target_system,
                                 connection.target_component,
                                 mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                                 0,
                                 1, 13,
                                 0, 0, 0, 0, 0, 0)

msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)

# GO TO GPS LOCATION
    

# START ARUCO CONTROL LOOP
aruco.start_control()



while 1:
    msg = connection.recv_match(
        type='LOCAL_POSITION_NED', blocking=True)
    print(msg)