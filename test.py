from time import sleep

from tools.agv_tools import AgvTools

DIR = 18
LEFT = 24
RIGHT = 23
FORWARD = 0
BACKWARD = 1
SPR = 400


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


def test2():
    # import pigpio

    pi = pigpio.pi()

    # pigpio sample rate of 4
    ramp = [[i, 5] for i in [50, 100, 200, 400, 625]]
    AgvTools.generate_ramp(
        pi=pi, ramp=ramp, motor_pin=RIGHT, clear_waves=False
    )
    AgvTools.generate_ramp(
        pi=pi, ramp=ramp, motor_pin=LEFT, clear_waves=False
    )

    # pi.set_PWM_dutycycle(LEFT, 128)
    # pi.set_PWM_dutycycle(RIGHT, 128)

    # freq = 500
    # pi.set_PWM_frequency(LEFT, freq)
    # pi.set_PWM_frequency(RIGHT, freq)

    try:
        while True:
            print(f"Right freq={pi.get_PWM_frequency(RIGHT)}")
            print(f"Left freq={pi.get_PWM_frequency(LEFT)}")
            sleep(0.5)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Stopping PIGPIO and exitting...")
    finally:
        pi.set_PWM_dutycycle(LEFT, 0)
        pi.set_PWM_dutycycle(RIGHT, 0)
        pi.wave_clear()
        pi.stop()


if __name__ == "__main__":
    test2()
