from typing import Any
from enum import Enum


class Zone(Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"


class Connection:
    def __init__(self, edge_1: "Hub", edge_2: "Hub",
                 max_link_capacity: int = 1):
        self.edge_1: Hub = edge_1
        self.edge_2: Hub = edge_2
        self.max_link_capacity: int = max_link_capacity

    def __str__(self) -> str:
        return (f"{self.edge_1.name}-{self.edge_2.name}, "
                f"max link: {self.max_link_capacity}")

    def __repr__(self) -> str:
        return self.__str__()

    def other_hub(self, actual_hub: "Hub"):
        if self.edge_1 == actual_hub:
            return self.edge_2
        else:
            return self.edge_1


class Hub:
    class Drone:
        def __init__(self, id: int):
            self.__id = id
            self.route: list[tuple] = []

        def get_id(self) -> int:
            return self.__id

        def __str__(self) -> str:
            result = f"id: {self.__id}, route: ["
            for hub in self.route:
                result += f"[{hub[0].name}, {hub[1]}]"
            result += "]"
            return result

        def __repr__(self) -> str:
            return f"- {self.__str__}"

    def __init__(self, name: str, x: int, y: int, type_of_hub: int = 0,
                 zone: Zone = Zone.normal, color: Any = None,
                 max_drones: int = 1):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.type_of_hub: int = type_of_hub
        self.zone: Zone = zone
        self.color: Any = color
        if color == "rainbow":
            self.color = "pink"
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

    def calculate_hub_cost(self) -> int:
        if self.zone.name == "normal":
            return 1
        elif self.zone.name == "blocked":
            return -1
        elif self.zone.name == "restricted":
            return 2
        elif self.zone.name == "priority":
            return 1

    def calculate_route(self, drone: "Hub.Drone", heuristic: dict[str, int]):
        cost: int = 100000
        actual_hub: Hub = self
        next_hub: Hub = self
        while (heuristic.get(actual_hub.name, 1) != 0):
            for connection in actual_hub.connections:
                temp_hub = connection.other_hub(actual_hub)
                if heuristic.get(temp_hub.name, 0) < cost:
                    cost = heuristic.get(temp_hub.name, 0)
                    next_hub = temp_hub
            actual_hub = next_hub
            drone.route.append(tuple([actual_hub, cost]))

    def create_drones(self, nb_drones: int) -> None:
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
