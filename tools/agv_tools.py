import math

# unit: inch
WHEEL_DIAM = 5

# steps per revolution
STEP_DRIVER_FREQ = 400

# unit: degrees
STEP_ANGLE = 360 / STEP_DRIVER_FREQ


class AgvTools:
    def calc_pulse_freq(velocity: float = 2.25) -> int:

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
