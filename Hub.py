from typing import Any
from enum import Enum


class Zone(Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"


class Connection:
    """Class for making connections between Hubs

    Args:
    - edge_1: first hub of the connection
    - edge_2: second hub of the connection
    - max_link_capacity: maximun quantity of drones that can be on a connection
    """
    wait_connection: Any = None

    def __init__(self, edge_1: "Hub", edge_2: "Hub",
                 max_link_capacity: int = 1):
        self.edge_1: Hub = edge_1
        self.edge_2: Hub = edge_2
        self.max_link_capacity: int = max_link_capacity

    def __str__(self) -> str:
        return (f"{self.edge_1.name}-{self.edge_2.name}, "
                f"max link: {self.max_link_capacity}")

    def __repr__(self) -> str:
        return f"[{self.__str__()}]"

    def other_hub(self, actual_hub: "Hub"):
        """function that takes a hub and return the other hub of the link"""
        if self.edge_1 == actual_hub:
            return self.edge_2
        else:
            return self.edge_1

    @classmethod
    def wait(cls) -> Any:
        """Function for returning the unique wait connection for waiting"""
        if cls.wait_connection is None:
            cls.wait_connection = Connection(Hub.wait(), Hub.wait(), 100000000)
        return cls.wait_connection

    def check_connection_constraint(
            self, drone: "Hub.Drone", g: int,
            constraints: list[tuple]) -> bool:
        """Function for checking a connection based on the constraints"""
        for constraint in constraints:
            if isinstance(constraint[1], Connection):
                if (constraint[0] == drone
                        and constraint[1] is self and constraint[2] == g):
                    return True
        return False


class Hub:
    """A class representing a hub

    Args:
    - name: the unique name of the hub
    - x: horizontal coordinate
    - y: vertical coordinate
    - type_of_hub: a integer representing the type of hub between 3 hubs:
        - type_of_hub = 0: normal hub
        - type_of_hub = 1: start hub
        - type_of_hub = 2: end hub
    """
    wait_Hub: Any = None

    class Drone:
        """A class representing each drone by an id

        Args:
        - id: an integer representing an identifier of the drone
        """

        def __init__(self, id: int):
            self.__id = id

        def get_id(self) -> int:
            return self.__id

        def __str__(self) -> str:
            return f"id: {self.__id}"

        def __repr__(self) -> str:
            return self.__str__()

        def __eq__(self, other: Any) -> bool:
            return self.get_id() == other.get_id()

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

    def move_to(self, drone_id: int, next_hub: "Hub") -> None:
        next_hub: Hub
        exist: bool = False
        if next_hub is self.wait_Hub:
            return
        for connection in self.connections:
            temp_hub: Hub = connection.other_hub(self)
            if temp_hub is next_hub:
                exist = True
        if not exist:
            if self.name != "Wait" and next_hub.name != "Wait":
                print(
                    "There is not a connection between "
                    f"{self.name} and {next_hub.name}")
            return
        for i in range(len(self.drones)):
            if self.drones[i].get_id() == drone_id:
                next_hub.drones.append(self.drones.pop(i))
                return

    @classmethod
    def wait(cls) -> Any:
        if cls.wait_Hub is None:
            cls.wait_Hub = Hub("Wait", 0, 0, -1, Zone.normal,
                               max_drones=10000000)
        return cls.wait_Hub

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

    def check_hub_contraint(self, drone: "Hub.Drone", g: int,
                            constraints: list[tuple]) -> bool:
        for constraint in constraints:
            if isinstance(constraint[1], str):
                if (constraint[0] == drone
                        and constraint[1] == self.name and constraint[2] == g):
                    return True
        return False

    def calculate_route(
            self, drone: "Hub.Drone", heuristic: dict[str, int],
            constraints: list[tuple]) -> list[tuple]:
        g: int = 1
        actual_hub: Hub = self
        route: list[tuple] = []
        while (actual_hub.type_of_hub != 2):
            next_is_priority: bool = False
            t = heuristic.get(actual_hub.name, 0) + g
            next_connection = Connection.wait()
            next_hub: Hub = actual_hub

            for connection in actual_hub.connections:
                temp_hub = connection.other_hub(actual_hub)
                if heuristic.get(temp_hub.name, 0) + g < t:
                    if (temp_hub.check_hub_contraint(drone, g, constraints)
                            or connection.check_connection_constraint(
                                drone, g, constraints)):
                        continue
                    t = heuristic.get(temp_hub.name, 0) + g
                    next_connection = connection
                    next_hub = temp_hub
                elif heuristic.get(temp_hub.name, 0) + g == t:
                    if (temp_hub.check_hub_contraint(drone, g, constraints)
                            or connection.check_connection_constraint(
                                drone, g, constraints)):
                        continue
                    if (temp_hub.zone == Zone.priority
                            and not next_is_priority):
                        t = heuristic.get(temp_hub.name, 0) + g
                        next_connection = connection
                        next_hub = temp_hub
                        next_is_priority = True

            if next_hub is actual_hub:
                next_connection = Connection.wait()
            actual_hub = next_hub
            route.append(tuple([actual_hub.name, g, next_connection]))
            g += actual_hub.calculate_hub_cost()
        return route

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

    def __repr__(self) -> str:
        return self.__str__()
