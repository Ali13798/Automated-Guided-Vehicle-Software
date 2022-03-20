import json
from dataclasses import dataclass


@dataclass
class ControllerConfig:
    gui_x_dimension: int
    gui_y_dimension: int
    title: str
    font_size: int
    padding: int


def read_config(config_file: str) -> ControllerConfig:
    with open(config_file, "r") as file:
        data = json.load(file)
        return ControllerConfig(**data)
