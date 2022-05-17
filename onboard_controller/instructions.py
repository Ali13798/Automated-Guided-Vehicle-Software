"""
File:       onboard_controller/instructions.py
Author:     Ali Karimiafshar
"""

from dataclasses import dataclass


@dataclass
class Instruction:
    command: str
    value: float
