from typing import Any
from enum import Enum


class Zone(Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    prioriy = "priority"


class Connection:
    def __init__(self, edge_1: "Hub", edge_2: "Hub",
                 max_link_capacity: int = 1):
        self.edge_1: Hub = edge_1
        self.edge_2: Hub = edge_2
        self.max_link_capacity: int = max_link_capacity


class Hub:

    def __init__(self, name: str, x: int, y: int, type_of_hub: int = 0,
                 zone: Zone = Zone.normal, color: Any = None,
                 max_drones: int = 1):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.type_of_hub: int = 0
        self.zone: Zone = zone
        self.color: Any = color
        self.max_drones: int = max_drones
        self.connections: list[Connection] = []

    def add_connection(self, new_connection: Connection):
        self.connections.append(new_connection)

    def __str__(self):
        return (
            f"Name: {self.name}, [{self.x}, {self.y}], zone: {self.zone}, "
            f"color: {self.color}, max drones: {self.max_drones}")
