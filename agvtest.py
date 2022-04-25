from time import sleep

import gpiozero

from tools.agv_tools import AgvTools

direction_gpio_bcm = 18
left_motor_gpio_bcm = 24
right_motor_gpio_bcm = 23

freq = AgvTools.calc_pulse_freq(velocity=2.25)
duty_cycle = 1
print(f"frequency: {freq}\nduty cycle: {duty_cycle}")

direction = gpiozero.OutputDevice(direction_gpio_bcm)
left_motor = gpiozero.PWMOutputDevice(
    left_motor_gpio_bcm, initial_value=duty_cycle, frequency=freq
)
right_motor = gpiozero.PWMOutputDevice(
    right_motor_gpio_bcm, initial_value=duty_cycle, frequency=freq
)

direction.on()
left_motor.blink()
right_motor.blink()

input()
