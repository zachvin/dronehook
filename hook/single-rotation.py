#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# pin numbers
PWM     = 33
DIR     = 24
ENCA    = 21
ENCB    = 23

# global vars and constants
ROT     = 15

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
            target = pos + ROT
            pwm.ChangeDutyCycle(50)
            print(f'[INFO] Target position {target} (current {pos})')
            while pos < target:
                pass
            pwm.ChangeDutyCycle(0)
            print('[INFO] Target position reached')
        elif x == 'd':
            GPIO.output(DIR, 0)
            target = pos - ROT
            pwm.ChangeDutyCycle(50)
            print(f'[INFO] Target position {target} (current {pos})')
            while pos > target:
                pass
            pwm.ChangeDutyCycle(0)
        else:
            break

finally:
    GPIO.cleanup()
