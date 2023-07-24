#!/usr/bin/env python3

# Movement signal handling for Dronehook
# Version 0.5
# Zach Vincent (zvincent@nd.edu)
# 07-17-23

PWM_CENTER  = 1500
PWM_RANGE_X = 300
PWM_RANGE_Y = 400


def set_rc_channel_pwm(connection, channel_id, pwm=1500):
    """ Set RC channel pwm value
    Args:
        channel_id (TYPE): Channel ID
        pwm (int, optional): Channel pwm value 1100-1900
    """
    if channel_id < 1 or channel_id > 18:
        print("Channel does not exist.")
        return

    rc_channel_values = [65535 for _ in range(18)]
    rc_channel_values[channel_id - 1] = pwm
    connection.mav.rc_channels_override_send(
        connection.target_system,                # target_system
        connection.target_component,             # target_component
        *rc_channel_values)                  # RC channel list, in microseconds.
    

def get_pwm(err_x:float, err_y:float, delta_x:int, delta_y:int) -> int:
    # error > 0 means plane must move up/left
    # error < 0 means plane must move down/right

    # higher PWM value means up/right
    # lower PWM value means down/left

    # err_x < 0     higher roll PWM
    # err_x > 0     lower roll PWM
    # err_y < 0     lower pitch PWM
    # err_y > 0     higher pitch PWM

    # determine actual PWM
    pwm_x = pwm_y = PWM_CENTER
    if err_x < 0:
        pwm_x = PWM_CENTER + delta_x
    else:
        pwm_x = PWM_CENTER - delta_x

    if err_y < 0:
        pwm_y = PWM_CENTER - delta_y
    else:
        pwm_y = PWM_CENTER - delta_y

    return pwm_x, pwm_y
    
def calculate_pwm_linear(connection, err_x:float, err_y:float) -> None:
    """ Calculate PWM values based on marker error and linear function
    Args:
        connection: Jetson to Ardupilot on Cube connection
        err_x (float): X error as ratio of half screen width
        err_y (float): Y error as ratio of half screen height
    """

    # how much PWM value will change from center
    delta_x = int(abs(err_x * PWM_RANGE_X))
    delta_y = int(abs(err_y * PWM_RANGE_Y))

    # get target PWM values
    pwm_x, pwm_y = get_pwm(err_x, err_y, delta_x, delta_y)
    
    # set PWM
    set_rc_channel_pwm(connection, 1, pwm_x)
    set_rc_channel_pwm(connection, 2, pwm_y)


def calculate_pwm_parabolic(connection, err_x:float, err_y:float) -> None:
    """ Calculate PWM values based on marker error and x^2 function
    Args:
        connection: Jetson to Ardupilot on Cube connection
        err_x (float): X error as ratio of half screen width
        err_y (float): Y error as ratio of half screen height
    """

    # how much PWM value will change from center
    delta_x = pow(err_x, 2) * PWM_RANGE_X
    delta_y = pow(err_y, 2) * PWM_RANGE_Y

    # get target PWM values
    pwm_x, pwm_y = get_pwm(err_x, err_y, delta_x, delta_y)

    # set PWM
    set_rc_channel_pwm(connection, 1, pwm_x)
    set_rc_channel_pwm(connection, 2, pwm_y)
