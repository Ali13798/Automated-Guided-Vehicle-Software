import math

# unit: inch
WHEEL_DIAM = 5

# steps per revolution
STEP_DRIVER_STEPS_PER_REV = 40

# unit: degrees
STEP_ANGLE = 360 / STEP_DRIVER_STEPS_PER_REV

MAX_VELOCITY = 2.25


class AgvTools:
    def calc_pulse_freq(velocity: float = MAX_VELOCITY) -> int:

        # unit: in/s
        velocity_inps = velocity * 12

        # unit: radians/s
        omega_rps = velocity_inps / (WHEEL_DIAM / 2)

        # unit: degrees/s
        omega_dps = omega_rps * 180 / math.pi

        # unit: 1/s (Hz)
        pulse_freq = omega_dps / STEP_ANGLE

        return int(round(pulse_freq, 0))

    def calc_pulse_num(inches: float) -> float:
        # radians
        angle = inches / (WHEEL_DIAM / 2)

        # degrees
        angle = angle * 180 / math.pi

        return angle / STEP_ANGLE

    def accelerate(time: float = 5.0):
        return
        ms = round(time * 1000)
        v0 = 0
        vf = MAX_VELOCITY
        steps = ms / 250
        for i in range(1, steps):
            v = 0
            AgvTools.calc_pulse_freq()
