from pymavlink import mavutil
import time

# start connection
# 14550 - typically default mavlink connection stream
# SITL creates two ports so the primary one we'll use for ground station software
the_connection = mavutil.mavlink_connection('udpin:localhost:14551')


# ==================
# wait for heartbeat
# ==================
the_connection.wait_heartbeat()
print(f'Heartbeat from system (system {the_connection.target_system} component {the_connection.target_component})')


# ===
# arm
# ===
the_connection.mav.command_long_send(the_connection.target_system, the_connection.target_component, mavutil.mavlink.MAV_CMD_COMPONENT_ARM_DISARM,
                                     0, 1,  0,    0, 0, 0, 0, 0)

msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)

time.sleep(2)

# =======
# takeoff
# =======
print('Initiating takeoff')
the_connection.mav.command_int_send(the_connection.target_system, the_connection.target_component, 0, mavutil.mavlink.MAV_CMD_NAV_TAKEOFF_LOCAL,
                                     0, 0, 10, 0, 0, 0, 0, 0, 20)

msg = the_connection.recv_match(type='COMMAND_ACK', blocking=True)
print(msg)