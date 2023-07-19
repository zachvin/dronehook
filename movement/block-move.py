'''
from pymavlink import mavutil

def turn_left(con):
    con.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, con.target_system,
                                                                               con.target_component,
                                                                               mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                                                                               int(0b010111111111),
                                                                               0, 0, 0,
                                                                               0, 0, 0,
                                                                               0, 0, 0,
                                                                               0, 2))
    
    return(con.recv_match(type='COMMAND_ACK', blocking=True))

    
def turn_right(con):
    con.mav.send(
        mavutil.mavlink.MAVLink_set_position_target_local_ned_message(10, con.target_system,
                                                                               con.target_component,
                                                                               mavutil.mavlink.MAV_FRAME_LOCAL_NED,
                                                                               int(0b010111111111),
                                                                               0, 0, 0,
                                                                               0, 0, 0,
                                                                               0, 0, 0,
                                                                               0, 2))
    return(con.recv_match(type='COMMAND_ACK', blocking=True))

def turn_right_cond(con):
    con.mav.send(
        mavutil.mavlink.MAVLink_
    )

# start connection
# 14550 - typically default mavlink connection stream
# SITL creates two ports so the primary one we'll use for ground station software
the_connection = mavutil.mavlink_connection('udpin:localhost:14551')


# wait for first heartbeat. sets system and component ID of remote system for the link
the_connection.wait_heartbeat()
print(f'Heartbeat from system (system {the_connection.target_system} component {the_connection.target_component})')


# turn left
print('Turning left...')
print(turn_left(the_connection))

while True:
    msg = the_connection.recv_match(blocking=True)
    print(msg)

# turn right
print('Turning right...')
print(turn_right(the_connection))

while 1:
    msg = the_connection.recv_match(
        type='LOCAL_POSITION_NED', blocking=True)
    print(msg)
'''
from pymavlink import mavutil
import time

# Start a connection listening to a UDP port
connection = mavutil.mavlink_connection('/dev/ttyACM0')

# Wait for the first heartbeat
#   This sets the system and component ID of remote system for the link
connection.wait_heartbeat()
print("Heartbeat from system (system %u component %u)" %
      (connection.target_system, connection.target_component))


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
    

# set roll (channel 1)
print('Setting roll:')
set_rc_channel_pwm(1, 1200)
print('Success')

time.sleep(2)

print('Setting reroll')
# now set it chonky style
set_rc_channel_pwm(1, 1800)
print('Success')

while 1:
    msg = connection.recv_match(
        type='LOCAL_POSITION_NED', blocking=True)
    print(msg)
