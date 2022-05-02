import math

import pigpio

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

    def generate_ramp(
        pi: pigpio.pi, ramp: list[int, int], motor_pin: int, clear_waves: bool
    ):
        """Generate ramp wave forms.
        ramp:  List of [Frequency, Steps]

        Note: Sourced from https://www.rototron.info/raspberry-pi-stepper-motor-tutorial/
        """
        if clear_waves:
            pi.wave_clear()  # clear existing waves

        length = len(ramp)  # number of ramp levels
        wid = [-1] * length

        # Generate a wave per ramp level
        for i in range(length):
            frequency = ramp[i][0]
            micros = int(500000 / frequency)
            wf = []
            wf.append(pigpio.pulse(1 << motor_pin, 0, micros))  # pulse on
            wf.append(pigpio.pulse(0, 1 << motor_pin, micros))  # pulse off
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
