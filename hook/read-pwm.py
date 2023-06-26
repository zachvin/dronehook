#!/usr/bin/env python3

import RPi.GPIO as GPIO
import time

# pin numbers
PWM     = 33
DIR     = 24
ENCA    = 21
ENCB    = 23

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
