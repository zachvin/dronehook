#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# pin numbers
DIR     = 31 # prev: 24
PWM     = 33
ENCB    = 35 # prev: 23
ENCA    = 37 # prev: 21

# global vars and constants
SINGLE_ROT_TIME = 0.3 # prev: 1.68

pos     = 0

def read_encoder(pin):
    global pos

    b = GPIO.input(ENCB)
    if b > 0:
        pos -= 1
    else:
        pos += 1

    print(f'[INFO] Position: {pos}')


# map pins
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(ENCA, GPIO.IN)
GPIO.setup(ENCB, GPIO.IN)

# enable and turn on motor
GPIO.output(DIR, 1)
pwm = GPIO.PWM(PWM, 10000)
pwm.start(0)

# monitor encoder pins
GPIO.add_event_detect(ENCA, GPIO.RISING, callback=read_encoder)

try:
    while True:
        x = input()
        if x == 'a':
            GPIO.output(DIR, 1)
            pwm.ChangeDutyCycle(50)
            time.sleep(SINGLE_ROT_TIME)
            pwm.ChangeDutyCycle(0)
            print('[INFO] Target position reached')
        elif x == 'd':
            GPIO.output(DIR, 0)
            pwm.ChangeDutyCycle(50)
            time.sleep(5 * SINGLE_ROT_TIME)
            pwm.ChangeDutyCycle(0)
            print('[INFO] Target position reached')
        else:
            break

finally:
    GPIO.cleanup()
