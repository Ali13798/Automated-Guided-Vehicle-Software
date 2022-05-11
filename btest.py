from time import sleep

import gpiozero
import pigpio

from onboard_controller.pi_bcm_pin_assignment import Pin
from tools.agv_tools import AgvTools


class Test:
    def __init__(self) -> None:
        # Constants
        self.motors_gpio_bcm = Pin.motors.value
        left_direction_gpio_bcm = Pin.left_motor_backward_direction.value
        right_direction_gpio_bcm = Pin.right_motor_backward_direction.value
        left_motor_kill_switch = Pin.left_motor_kill_switch.value
        right_motor_kill_switch = Pin.right_motor_kill_switch.value

        # Assignments
        self.direction_left = gpiozero.OutputDevice(
            left_direction_gpio_bcm, active_high=False
        )
        self.direction_right = gpiozero.OutputDevice(right_direction_gpio_bcm)
        self.kill_right = gpiozero.OutputDevice(right_motor_kill_switch)
        self.kill_left = gpiozero.OutputDevice(left_motor_kill_switch)

        # Connect to pigpiod daemon. Must first execute the following
        # commands in a terminal window without " marks:
        # "sudo killall pigpiod"
        # "sudo pigpiod -t 0 -s 4"
        self.pi = pigpio.pi()

        # Set up pins as an output
        self.pi.set_mode(self.motors_gpio_bcm, pigpio.OUTPUT)

        # rising edge counter
        self.cb_counter = self.pi.callback(user_gpio=self.motors_gpio_bcm)

        # FOrward = off, backward = on
        self.direction_left.off()
        self.direction_right.off()

        # stop the wheel = on
        self.kill_right.off()
        self.kill_left.off()

        self.go(self.pi)

    def go(self, pi):
        # distance in inches to travel or arc length of turn
        dist = 100
        ramp = AgvTools.create_ramp_inputs(inches=dist)
        print(ramp)

        AgvTools.generate_ramp(
            pi=pi, ramp=ramp, motor_pin=self.motors_gpio_bcm, clear_waves=True
        )

        # input("Press enter to exit the program. Do not exit mid execution.")
        print(
            f"final pulse count is: {self.cb_counter.tally()}\nExpected: {AgvTools.calc_pulse_num_from_dist(inches=dist)}"
        )
        self.pi.wave_clear()


def main():
    t = Test()
    input()
    print(t.cb_counter.tally())
    input()


if __name__ == "__main__":
    main()
