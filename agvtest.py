from time import sleep

import gpiozero

from onboard_controller.pi_bcm_pin_assignment import Pin
from tools.agv_tools import AgvTools

left_direction_gpio_bcm = Pin.left_motor_backward_direction.value
right_direction_gpio_bcm = Pin.right_motor_backward_direction.value
left_motor_kill_switch = Pin.left_motor_kill_switch.value
right_motor_kill_switch = Pin.right_motor_kill_switch.value

motors_gpio_bcm = Pin.motors.value

freq = AgvTools.calc_pulse_freq(velocity=2.25)
freq = 2000
duty_cycle = 1
print(f"frequency: {freq}\nduty cycle: {duty_cycle}")

freq = freq * 2
direction_left = gpiozero.OutputDevice(
    left_direction_gpio_bcm, active_high=False
)
direction_right = gpiozero.OutputDevice(right_direction_gpio_bcm)
kill_right = gpiozero.OutputDevice(right_motor_kill_switch)
kill_left = gpiozero.OutputDevice(left_motor_kill_switch)
motors = gpiozero.PWMOutputDevice(
    motors_gpio_bcm, initial_value=duty_cycle, frequency=freq
)

direction_left.off()
direction_right.off()

kill_right.off()
kill_left.off()

motors.blink(on_time=1 / freq, off_time=1 / freq)

input()
