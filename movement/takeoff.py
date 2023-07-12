from pymavlink import mavutil
import time

# start connection
# 14550 - typically default mavlink connection stream
# SITL creates two ports so the primary one we'll use for ground station software
connection = mavutil.mavlink_connection('udpin:localhost:14551')


# wait for first heartbeat. sets system and component ID of remote system for the link
connection.wait_heartbeat()
print(f'Heartbeat from system (system {connection.target_system} component {connection.target_component})')

# the_connection.target_system is the aircraft which is autofilled
# when waiting for heartbeat
connection.mav.command_long_send(connection.target_system, connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                     0, 1,  0,    0, 0, 0, 0, 0)
                                    #   arm:force

msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)

# takeoff
print('Taking off...')
connection.mav.command_long_send(connection.target_system, connection.target_component, mavutil.mavlink.MAV_CMD_DO_SET_MODE,
                                     0,
                                     1, 13,
                                     0, 0, 0, 0, 0, 0)

msg = connection.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)