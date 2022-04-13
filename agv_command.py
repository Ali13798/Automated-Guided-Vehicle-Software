from enum import Enum, auto


class AgvCommand(Enum):
    invalid = "!INVALID"
    valid = "!VALID"
    forward = "FORWARD"
    backward = "BACKWARD"
    rotate_cw = "ROTATECW"
    rotate_ccw = "ROTATECCW"
    calibrate_home = "CALIBRATEHOME"
