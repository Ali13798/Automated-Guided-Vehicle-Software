"""
File:       stationary_controller/mode.py
Author:     Ali Karimiafshar
"""

from enum import Enum, auto


class Mode(Enum):
    Teach = auto()
    Production = auto()
    Unselected = auto()
