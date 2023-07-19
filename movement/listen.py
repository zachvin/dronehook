from pymavlink import mavutil

# start connection
# 14550 - typically default mavlink connection stream
# SITL creates two ports so the primary one we'll use for ground station software

# for Jetson:   /dev/ttyACM0
# for SITL:     127.0.0.1:14551
the_connection = mavutil.mavlink_connection('/dev/ttyACM0')


# wait for first heartbeat. sets system and component ID of remote system for the link
the_connection.wait_heartbeat()
print(f'Heartbeat from system (system {the_connection.target_system} component {the_connection.target_component})')

while True:
    msg = the_connection.recv_match(blocking=True)
    print(msg)
