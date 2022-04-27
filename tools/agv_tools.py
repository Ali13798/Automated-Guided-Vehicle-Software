import math

import gpiozero

# unit: inch
WHEEL_DIAM = 5

# steps per revolution
STEP_DRIVER_STEPS_PER_REV = 400

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

        # Double since on and off times are separate.
        return int(round(pulse_freq, 0)) * 2

    def calc_pulse_num_from_dist(inches: float) -> int:
        angle_r = inches / (WHEEL_DIAM / 2)
        angle_d = angle_r * 180 / math.pi
        return int(round(angle_d / STEP_ANGLE, 0))

    def calc_pulse_num_from_freq(freq: float, time_ms: int) -> int:
        return math.floor(freq * time_ms / 1000)

    def calc_arc_pulse_num(angle: int) -> int:
        rad = angle / 180 * math.pi
        arc_length = WHEEL_DIAM / 2 * rad
        return AgvTools.calc_pulse_num_from_dist(arc_length)
