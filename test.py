from time import sleep

import RPi.GPIO as GPIO

DIR = 18
LEFT = 24
RIGHT = 23
FORWARD = 0
BACKWARD = 1
SPR = 400

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR, GPIO.OUT)
GPIO.setup(LEFT, GPIO.OUT)
GPIO.setup(RIGHT, GPIO.OUT)

GPIO.output(DIR, FORWARD)

step_count = SPR
delay = 1 / SPR

for x in range(step_count):
    GPIO.output(LEFT, GPIO.HIGH)
    GPIO.output(RIGHT, GPIO.HIGH)
    sleep(delay)
    GPIO.output(LEFT, GPIO.LOW)
    GPIO.output(RIGHT, GPIO.LOW)
    sleep(delay)

sleep(0.5)
GPIO.output(DIR, BACKWARD)
for x in range(step_count):
    GPIO.output(LEFT, GPIO.HIGH)
    GPIO.output(RIGHT, GPIO.HIGH)
    sleep(delay)
    GPIO.output(LEFT, GPIO.LOW)
    GPIO.output(RIGHT, GPIO.LOW)
    sleep(delay)
