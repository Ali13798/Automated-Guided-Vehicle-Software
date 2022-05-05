from time import sleep

import gpiozero

from onboard_controller.pi_bcm_pin_assignment import Pin
from tools.agv_tools import AgvTools

left_direction_gpio_bcm = Pin.left_motor_backward_direction.value
right_direction_gpio_bcm = Pin.right_motor_backward_direction.value
motors_gpio_bcm = Pin.motors.value

freq = AgvTools.calc_pulse_freq(velocity=2.25)
freq = 20
duty_cycle = 1
print(f"frequency: {freq}\nduty cycle: {duty_cycle}")

direction_left = gpiozero.OutputDevice(left_direction_gpio_bcm)
direction_right = gpiozero.OutputDevice(right_direction_gpio_bcm)
motors = gpiozero.PWMOutputDevice(
    motors_gpio_bcm, initial_value=duty_cycle, frequency=freq
)

direction_left.on()
direction_right.on()

motors.blink(on_time=1 / freq, off_time=1 / freq)

input()
