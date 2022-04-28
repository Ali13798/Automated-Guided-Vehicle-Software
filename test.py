from time import sleep

DIR = 18
LEFT = 24
RIGHT = 23
FORWARD = 0
BACKWARD = 1
SPR = 400


def test2():
    import pigpio

    pi = pigpio.pi()

    pi.set_PWM_dutycycle(LEFT, 128)
    pi.set_PWM_dutycycle(RIGHT, 128)

    freq = 500
    pi.set_PWM_frequency(LEFT, freq)
    pi.set_PWM_frequency(RIGHT, freq)

    try:
        while True:
            sleep(1)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Stopping PIGPIO and exitting...")
    finally:
        pi.set_PWM_dutycycle(LEFT, 0)
        pi.set_PWM_dutycycle(RIGHT, 0)
        pi.stop()


def test1():
    import RPi.GPIO as GPIO

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


if __name__ == "__main__":
    test2()
