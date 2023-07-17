#!/usr/bin/env python3

# Movement signal handling for Dronehook
# Version 0.5
# Zach Vincent (zvincent@nd.edu)
# 07-17-23

PWM_CENTER  = 1500
PWM_RANGE   = 500

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
    
def calculate_pwm_linear(connection, err_x:float, err_y:float) -> None:
    """ Calculate PWM values based on marker error and linear function
    Args:
        err_x (float): X error as ratio of half screen width
        err_y (float): Y error as ratio of half screen height
    """

    # error > 0 means plane must move up/left
    # error < 0 means plane must move down/right

    # higher PWM value means down/right
    # lower PWM value means up/left

    pwm_x = PWM_CENTER + (err_x * PWM_RANGE)
    pwm_y = PWM_CENTER + (err_y * PWM_RANGE)

    set_rc_channel_pwm(connection, 1, pwm_x)
    set_rc_channel_pwm(connection, 2, pwm_y)


def calculate_pwm_cubic(connection, err_x:float, err_y:float) -> None:
    """ Calculate PWM values based on marker error and x^3 function
    Args:
        err_x (float): X error as ratio of half screen width
        err_y (float): Y error as ratio of half screen height
    """

    pwm_x = PWM_CENTER + (pow(err_x, 3) * PWM_RANGE)
    pwm_y = PWM_CENTER + (pow(err_y, 3) * PWM_RANGE)

    set_rc_channel_pwm(connection, 1, pwm_x)
    set_rc_channel_pwm(connection, 2, pwm_y)
