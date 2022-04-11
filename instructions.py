from dataclasses import dataclass


@dataclass
class Instruction:
    command: str
    value: float
