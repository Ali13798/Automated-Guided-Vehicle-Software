from enum import Enum


class Pin(Enum):
    motors = 23
    right_motor_backward_direction = 26
    left_motor_backward_direction = 18
    left_motor_kill_switch = 22
    right_motor_kill_switch = 12
