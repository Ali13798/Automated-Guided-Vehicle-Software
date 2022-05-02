from time import sleep

from tools.agv_tools import AgvTools

DIR = 18
# LEFT = 24
RIGHT = 23
FORWARD = 0
BACKWARD = 1
SPR = 400


MOTOR = 23
KILL_RIGHT = 24
KILL_LEFT = 25


def test1():
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(DIR, GPIO.OUT)
    # GPIO.setup(LEFT, GPIO.OUT)
    GPIO.setup(MOTOR, GPIO.OUT)
    GPIO.setup(KILL_RIGHT, GPIO.OUT)
    GPIO.setup(KILL_LEFT, GPIO.OUT)

    GPIO.output(DIR, FORWARD)

    step_count = SPR
    delay = 1 / SPR

    for x in range(step_count):
        # GPIO.output(LEFT, GPIO.HIGH)
        GPIO.output(MOTOR, GPIO.HIGH)
        sleep(delay)
        # GPIO.output(LEFT, GPIO.LOW)
        GPIO.output(MOTOR, GPIO.LOW)
        sleep(delay)

    sleep(0.5)
    GPIO.output(DIR, BACKWARD)
    for x in range(step_count):
        # GPIO.output(LEFT, GPIO.HIGH)
        GPIO.output(MOTOR, GPIO.HIGH)
        sleep(delay)
        # GPIO.output(LEFT, GPIO.LOW)
        GPIO.output(MOTOR, GPIO.LOW)
        sleep(delay)


def test2():
    import pigpio

    pi = pigpio.pi()

    # pigpio sample rate of 4
    ramp = [[i, 5] for i in [50, 100, 200, 400, 625]]
    AgvTools.generate_ramp(
        pi=pi, ramp=ramp, motor_pin=RIGHT, clear_waves=False
    )
    # AgvTools.generate_ramp(
    #     pi=pi, ramp=ramp, motor_pin=LEFT, clear_waves=False
    # )

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
        # pi.set_PWM_dutycycle(LEFT, 0)
        pi.set_PWM_dutycycle(RIGHT, 0)
        pi.wave_clear()
        pi.stop()


def test3():
    from time import sleep

    import pigpio

    MOTOR = 23
    DIR = 18

    # Connect to pigpiod daemon
    pi = pigpio.pi()

    # Set up pins as an output
    pi.set_mode(DIR, pigpio.OUTPUT)
    pi.set_mode(MOTOR, pigpio.OUTPUT)

    rampup = [[i, 50] for i in [50, 100, 200, 400, 625]]
    rampdown = rampup.copy()
    rampdown.reverse()

    #! Experiment
    # SWITCH = 0
    # pi.set_mode(SWITCH, pigpio.INPUT)

    try:
        old_ramp = 0
        while True:
            #! Experiment
            # new_ramp = pi.read(SWITCH)
            new_ramp = input("Enter 0 for up or 1 for down: ")

            if int(new_ramp) == old_ramp:
                sleep(0.5)
                continue

            if new_ramp:
                AgvTools.generate_ramp(rampup)
            else:
                AgvTools.generate_ramp(rampdown)
            old_ramp = new_ramp

            print(f"Right freq={pi.get_PWM_frequency(MOTOR)}")
            sleep(0.5)
    except KeyboardInterrupt:
        print("\nCtrl-C pressed. Stopping PIGPIO and exitting...")
    finally:
        pi.wave_clear()
        pi.stop()


if __name__ == "__main__":
    test1()
