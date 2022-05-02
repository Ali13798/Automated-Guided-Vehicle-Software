from time import sleep

import pigpio

from tools.agv_tools import AgvTools

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
SWITCH = 12
pi.set_mode(SWITCH, pigpio.INPUT)

try:
    old_ramp = 0
    while True:
        #! Experiment
        new_ramp = pi.read(SWITCH)
        # new_ramp = input("Enter 0 for up or 1 for down: ")

        if int(new_ramp) == old_ramp:
            sleep(0.5)
            continue

        if new_ramp:
            AgvTools.generate_ramp(
                pi=pi, motor_pin=MOTOR, ramp=rampup, clear_waves=True
            )
        else:
            AgvTools.generate_ramp(
                pi=pi, motor_pin=MOTOR, ramp=rampdown, clear_waves=True
            )
        old_ramp = new_ramp

        print(f"Right freq={pi.get_PWM_frequency(MOTOR)}")
        sleep(0.5)
except KeyboardInterrupt:
    print("\nCtrl-C pressed. Stopping PIGPIO and exitting...")
finally:
    pi.wave_clear()
    pi.stop()
