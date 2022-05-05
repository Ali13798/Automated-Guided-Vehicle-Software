from enum import Enum, auto


class AgvCommand(Enum):
    invalid_command = "!INVALID"
    valid_command = "!VALID"
    e_stop = "!ESTOP"
    set_mode = "!SETMODE"

    forward = "FORWARD"
    backward = "BACKWARD"
    rotate_cw = "ROTATECW"
    rotate_ccw = "ROTATECCW"
    calibrate_home = "CALIBRATEHOME"
