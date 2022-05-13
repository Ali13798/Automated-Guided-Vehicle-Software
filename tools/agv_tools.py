import math

import pigpio
from onboard_controller.pi_bcm_pin_assignment import Pin

# unit: inch
WHEEL_DIAM = 5
TURN_RADIUS = 16

# steps per revolution
STEP_DRIVER_STEPS_PER_REV = 3200

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

    def calc_arc_length(angle: int) -> float:
        rad = angle / 180 * math.pi
        arc_length = TURN_RADIUS * rad
        return arc_length

    def create_ramp_inputs(
        inches: float, remain_pulse: int = -1
    ) -> list[list[int, int]]:
        """Generates the acceleration and deceleration frequencies.

        Args:
            inches (float): distance to be traversed.

        Returns:
            list[list[int, int]]: list[list[frequency, steps]]
        """
        output: list[list[int, int]] = []
        # freq_levels = [50, 100, 160, 200, 320, 400, 500, 800, 1000, 1600]
        freq_levels = [50, 100, 200, 400, 500, 625, 1000, 1250, 2000]
        freq_levels = [2000]  # for testing
        steps_per_freq_level = 100

        pulse_num = (
            AgvTools.calc_pulse_num_from_dist(inches=inches)
            if remain_pulse == -1
            else remain_pulse
        )

        freq_level_index = pulse_num // (steps_per_freq_level * 2)

        coast_pulse_num = pulse_num - (freq_level_index * 20)

        if not freq_level_index < len(freq_levels):
            freq_level_index = len(freq_levels) - 1

        coast_pulse_num = pulse_num - (
            freq_level_index * steps_per_freq_level * 2
        )

        for freq_level in freq_levels[:freq_level_index]:
            output.append([freq_level, steps_per_freq_level])

        if coast_pulse_num:
            output.append([freq_levels[freq_level_index], coast_pulse_num])

        for freq_level in reversed(freq_levels[:freq_level_index]):
            output.append([freq_level, steps_per_freq_level])

        return output

    def generate_ramp(
        pi: pigpio.pi,
        ramp: list[int, int],
        motor_pin: int,
        clear_waves: bool = True,
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

    def wave_clear(pi: pigpio.pi, motor: Pin.motors.value):
        f = 2000
        micros = int(500000 / f)
        wf = []
        wf.append(pigpio.pulse(1 << motor, 0, micros))  # pulse on
        wf.append(pigpio.pulse(0, 1 << motor, micros))  # pulse off
        pi.wave_add_generic(wf)
        wid = pi.wave_create()
        s = 1
        x = s & 255
        y = s >> 8
        chain = [255, 0, wid, 255, 1, x, y]
        pi.wave_chain(chain)


def main():
    print(AgvTools.create_ramp_inputs(inches=10))


if __name__ == "__main__":
    main()
