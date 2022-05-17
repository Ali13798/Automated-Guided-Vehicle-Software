"""
File:       tools/config.py
Author:     Ali Karimiafshar
"""

import json
from dataclasses import dataclass


@dataclass
class ControllerConfig:
    gui_x_dimension: int
    gui_y_dimension: int
    title: str
    font_size: int
    padding: int
    socket_encoding_format: str
    socket_message_header_size: int
    socket_disconnect_message: str
    socket_establish_connection_message: str


def read_config(
    config_file: str = "configurations.json",
) -> ControllerConfig:
    with open(config_file, "r") as file:
        data = json.load(file)
        return ControllerConfig(**data)
