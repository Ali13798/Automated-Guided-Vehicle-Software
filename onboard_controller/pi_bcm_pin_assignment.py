from enum import Enum


class Pin(Enum):
    motors = 23
    right_motor_backward_direction = 26
    left_motor_backward_direction = 18
    left_motor_kill_switch = 22
    right_motor_kill_switch = 12
    horizontal_os = 16
    left_vertical_os = 20
    right_vertical_os = 21
