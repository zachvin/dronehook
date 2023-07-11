#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# pin numbers
DIR     = 31
PWM     = 33
ENCB    = 35
ENCA    = 37

# map pins
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(ENCA, GPIO.IN)
GPIO.setup(ENCB, GPIO.IN)

# set direction and turn on motor
GPIO.output(DIR, 1)
pwm = GPIO.PWM(PWM, 100)
pwm.start(15)

while True:
    print(f'[INFO] Encoder A: {GPIO.input(ENCA)}')
    print(f'[INFO] Encoder B: {GPIO.input(ENCB)}')

    time.sleep(0.5)
