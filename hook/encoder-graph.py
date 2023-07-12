#!/usr/bin/env python3

import RPi.GPIO as GPIO
import matplotlib.pyplot as plt
import time

def read_encoder(pin):
    global ENCA, ENCB, enca_data, encb_data, num

    a = GPIO.input(ENCA)
    b = GPIO.input(ENCB)

    enca_data.append(a)
    encb_data.append(b)

    num += 1


# pin numbers
DIR     = 31
PWM     = 33
ENCB    = 35
ENCA    = 37

# global vars
enca_data = []
encb_data = []
num = 0

# map pins
GPIO.setmode(GPIO.BOARD)

GPIO.setup(PWM, GPIO.OUT)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(ENCA, GPIO.IN)
GPIO.setup(ENCB, GPIO.IN)

# set motor direction and pwm pin
GPIO.output(DIR, 1)
pwm = GPIO.PWM(PWM, 100)

# monitor encoder pin
GPIO.add_event_detect(ENCA, GPIO.RISING, callback=read_encoder)
GPIO.add_event_detect(ENCB, GPIO.RISING, callback=read_encoder)

try:
    pwm.start(25)

    # wait for n changes to encoder inputs
    while num < 20:
        print(num)

finally:
    GPIO.cleanup()

# show graph
plt.plot(enca_data, label='A')
plt.plot(encb_data, label='B')

plt.legend()

plt.show()
