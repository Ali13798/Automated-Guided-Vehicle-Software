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
testramp = [
    [10, 50],
    [10, 100],
    [10, 200],
    [10, 400],
    [18, 625],
    [10, 400],
    [10, 200],
    [10, 100],
    [10, 50],
]


def generate_ramp(
    ramp: list[int, int],
):
    """Generate ramp wave forms.
    ramp:  List of [Frequency, Steps]

    Note: Sourced from https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/
    """
    pi.wave_clear()  # clear existing waves

    length = len(ramp)  # number of ramp levels
    wid = [-1] * length

    # Generate a wave per ramp level
    for i in range(length):
        frequency = ramp[i][0]
        micros = int(500000 / frequency)
        wf = []
        wf.append(pigpio.pulse(1 << MOTOR, 0, micros))  # pulse on
        wf.append(pigpio.pulse(0, 1 << MOTOR, micros))  # pulse off
        pi.wave_add_generic(wf)
        wid[i] = pi.wave_create()

    # Generate a chain of waves
    chain = []
    for i in range(length):
        steps = ramp[i][1]
        x = steps & 255
        y = steps >> 8
        chain += [255, 0, wid[i], 255, 1, x, y]

    pi.wave_chain(chain)  # Transmit chain.


#! Experiment
SWITCH = 12
pi.set_mode(SWITCH, pigpio.INPUT)
pi.set_pull_up_down(MOTOR, pigpio.PUD_UP)

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
            generate_ramp(ramp=testramp)
            # AgvTools.generate_ramp(pi=pi, motor_pin=MOTOR, ramp=rampup, clear_waves=True)
        else:
            generate_ramp(ramp=testramp)
            # AgvTools.generate_ramp(pi=pi, motor_pin=MOTOR, ramp=rampup, clear_waves=True)
        old_ramp = new_ramp

        print(f"Right freq={pi.get_PWM_frequency(MOTOR)}")
        sleep(0.5)
except KeyboardInterrupt:
    print("\nCtrl-C pressed. Stopping PIGPIO and exitting...")
finally:
    pi.wave_clear()
    pi.stop()
