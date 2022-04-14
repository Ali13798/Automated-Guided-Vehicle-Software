from dataclasses import dataclass


@dataclass
class Waypoint:
    x: int
    y: int
    heading: int

    def __str__(self) -> str:
        return f"Waypoint(x={self.x:.2f}, y={self.y:.2f}, heading={self.heading:.1f})"
