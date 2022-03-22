from dataclasses import dataclass


@dataclass
class Waypoint:
    x: int
    y: int
    heading: int
