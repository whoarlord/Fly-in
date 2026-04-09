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

    def __str__(self):
        return (f"{self.edge_1.name}-{self.edge_2.name}, "
                f"max link: {self.max_link_capacity}")


class Hub:
    class Drone:
        def __init__(self, id: int):
            self.__id = id

        def get_id(self) -> int:
            return self.__id

    def __init__(self, name: str, x: int, y: int, type_of_hub: int = 0,
                 zone: Zone = Zone.normal, color: Any = None,
                 max_drones: int = 1):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.type_of_hub: int = type_of_hub
        self.zone: Zone = zone
        self.color: Any = color
        self.max_drones: int = max_drones
        self.drones: list[Hub.Drone] = []
        self.connections: list[Connection] = []

    def add_connection(self, new_connection: Connection) -> None:
        self.connections.append(new_connection)

    def check_connection_exist(self, hub_1: "Hub", hub_2: "Hub") -> bool:
        for connection in self.connections:
            if ((connection.edge_1 == hub_1
                 and connection.edge_2 == hub_2)
                or (connection.edge_1 == hub_2
                    and connection.edge_2 == hub_1)):
                return True
        return False

    def create_drones(self, nb_drones: int):
        if self.type_of_hub != 1:
            print("Only the start_hub can create drones")
        else:
            for i in range(nb_drones):
                drone: Hub.Drone = self.Drone(i)
                self.drones.append(drone)

    def __str__(self) -> str:
        result: str
        result = (f"Name: {self.name}, [{self.x}, "
                  f"{self.y}], zone: {self.zone}, "
                  f"color: {self.color}, max drones: {self.max_drones}")
        if len(self.connections) == 0:
            return result
        result += "\nConnections:\n"
        for connection in self.connections:
            result += "- " + connection.__str__() + "\n"
        return result
