import math

# unit: inch
WHEEL_DIAM = 5

# steps per revolution
STEP_DRIVER_FREQ = 400

# unit: degrees
STEP_ANGLE = 360 / STEP_DRIVER_FREQ


def calc_pulse_freq(velocity: float = 2.25):

    # unit: in/s
    velocity_inps = velocity * 12

    # unit: radians/s
    omega_rps = velocity_inps / (WHEEL_DIAM / 2)

    # unit: degrees/s
    omega_dps = omega_rps * 180 / math.pi

    # unit: 1/s (Hz)
    pulse_freq = omega_dps / STEP_ANGLE

    return pulse_freq


def main():
    freq = calc_pulse_freq()
    print(freq)


if __name__ == "__main__":
    main()
