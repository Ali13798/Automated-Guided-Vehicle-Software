from time import sleep

import gpiozero
import pigpio

from onboard_controller.pi_bcm_pin_assignment import Pin
from tools.agv_tools import AgvTools

# Constants
motors_gpio_bcm = Pin.motors.value
left_direction_gpio_bcm = Pin.left_motor_backward_direction.value
right_direction_gpio_bcm = Pin.right_motor_backward_direction.value
left_motor_kill_switch = Pin.left_motor_kill_switch.value
right_motor_kill_switch = Pin.right_motor_kill_switch.value

# Assignments
direction_left = gpiozero.OutputDevice(left_direction_gpio_bcm)
direction_right = gpiozero.OutputDevice(right_direction_gpio_bcm)
kill_right = gpiozero.OutputDevice(right_motor_kill_switch)
kill_left = gpiozero.OutputDevice(left_motor_kill_switch)

# Connect to pigpiod daemon. Must first execute the following
# commands in a terminal window without " marks:
# "sudo killall pigpiod"
# "sudo pigpiod -t 0"
pi = pigpio.pi()

# Set up pins as an output
pi.set_mode(motors_gpio_bcm, pigpio.OUTPUT)

# rising edge counter
cb_counter = pi.callback(user_gpio=motors_gpio_bcm)

# FOrward = off, backward = on
direction_left.off()
direction_right.off()

# stop the wheel = on
kill_right.off()
kill_left.off()

# distance in inches to travel or arc length of turn
dist = 100
ramp = AgvTools.create_ramp_inputs(inches=dist)
print(ramp)

AgvTools.generate_ramp(
    pi=pi, ramp=ramp, motor_pin=motors_gpio_bcm, clear_waves=True
)

input("Press enter to exit the program. Do not exit mid execution.")
print(
    f"final pulse count is: {cb_counter.tally()}\nExpected: {AgvTools.calc_pulse_num_from_dist(inches=dist)}"
)
pi.wave_clear()
