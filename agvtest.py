from time import sleep

import gpiozero

from tools.agv_tools import AgvTools

direction_gpio_bcm = 18
left_motor_gpio_bcm = 23
right_motor_gpio_bcm = 24

freq = AgvTools.calc_pulse_freq(velocity=2.25)
print(freq)

direction = gpiozero.OutputDevice(direction_gpio_bcm)
left_motor = gpiozero.PWMOutputDevice(
    left_motor_gpio_bcm, initial_value=0.5, frequency=freq
)
right_motor = gpiozero.PWMOutputDevice(
    right_motor_gpio_bcm, initial_value=0.5, frequency=freq
)

left_motor.blink()

input()
