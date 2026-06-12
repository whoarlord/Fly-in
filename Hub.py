from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from CT import Constraint, Checkpoint

from typing import Any, Optional
from enum import Enum


class Zone(Enum):
    normal = "normal"
    blocked = "blocked"
    restricted = "restricted"
    priority = "priority"


class Connection:
    """Class for making connections between Hubs

    Attributes:
        edge_1: first hub of the connection
        edge_2: second hub of the connection
        max_link_capacity: maximun quantity of drones that can be on a
            connection
    """
    wait_connection: Optional["Connection"] = None

    def __init__(self, edge_1: "Hub", edge_2: "Hub",
                 max_link_capacity: int = 1):
        self.edge_1: Hub = edge_1
        self.edge_2: Hub = edge_2
        self.max_link_capacity: int = max_link_capacity

    def get_edge_1(self) -> Hub:
        return self.edge_1

    def get_edge_2(self) -> Hub:
        return self.edge_2

    def get_max_link_capacity(self) -> int:
        return self.max_link_capacity

    def __str__(self) -> str:
        return (f"{self.edge_1.get_name()}-{self.edge_2.get_name()}")

    def __repr__(self) -> str:
        return f"[{self.__str__()}]"

    def other_hub(self, actual_hub: "Hub") -> "Hub":
        """function that takes a hub and return the other hub of the link"""
        if self.edge_1 == actual_hub:
            return self.edge_2
        else:
            return self.edge_1

    @classmethod
    def wait(cls) -> "Connection":
        """Function for returning the unique wait connection for waiting"""
        if cls.wait_connection is None:
            cls.wait_connection = Connection(Hub.wait(), Hub.wait(), 100000000)
        return cls.wait_connection

    def check_connection_constraint(
            self, drone: "Hub.Drone", f: int,
            constraints: list[Constraint], reach_zone: Zone) -> bool:
        """Function for checking a connection based on the constraints

        this function checks the constraints list, looking for a collision
        between de actual time and drone and the same time and drone at the
        list, if the function detects a collision return true, if it doesn't
        it return false.

        It also checks the f + 1, in the case the reach_zone is restricted.

        Args:
            drone (Hub.Drone): the drone being checked
            constraints (list[tuple]): the list with the constraints of the
                possible solution
            reach_zone (Zone): the zone of the next hub where the drone is
                    gonna move

        Returns:
            bool: a boolean for the constraints check result
        """
        for constraint in constraints:
            if isinstance(constraint[1], Connection):
                if (constraint[0] == drone
                        and constraint[1] is self and constraint[2] == f):
                    return True
                if (reach_zone.value == "restricted"):
                    if (constraint[0] == drone
                            and constraint[1] is self
                            and constraint[2] == f + 1):
                        return True
        return False


class Hub:
    """A class representing a hub

    Attributes:
        name: the unique name of the hub
        x: horizontal coordinate
        y: vertical coordinate
        type_of_hub: a integer representing the type of hub between 3 hubs:
        -   type_of_hub = 0: normal hub
        -   type_of_hub = 1: start hub
        -   type_of_hub = 2: end hub
    """
    wait_Hub: Optional["Hub"] = None

    class Drone:
        """A class representing each drone by an id

        Attributes:
            id: an integer representing an identifier of the drone
        """

        def __init__(self, id: int):
            self.__id = id

        def get_id(self) -> int:
            """Function for getting the drone id"""
            return self.__id

        def __str__(self) -> str:
            return f"id: {self.__id}"

        def __repr__(self) -> str:
            return self.__str__()

        def __eq__(self, other: object) -> bool:
            if not isinstance(other, Hub.Drone):
                return NotImplemented
            return self.get_id() == other.get_id()

    def __init__(self, name: str, x: int, y: int, type_of_hub: int = 0,
                 zone: Zone = Zone.normal, color: Any = None,
                 max_drones: int = 1):
        self.__name: str = name
        self.__x: int = x
        self.__y: int = y
        self.__type_of_hub: int = type_of_hub
        self.__zone: Zone = zone
        self.__color: Any = "pink" if color == "rainbow" else color
        self.__max_drones: int = max_drones
        self.drones: list[Hub.Drone] = []
        self.__connections: list[Connection] = []

    def get_name(self) -> str:
        return self.__name

    def get_x(self) -> int:
        return self.__x

    def add_x(self, to_add: int) -> None:
        self.__x += to_add

    def get_y(self) -> int:
        return self.__y

    def add_y(self, to_add: int) -> None:
        self.__y += to_add

    def get_type_of_hub(self) -> int:
        return self.__type_of_hub

    def get_zone(self) -> Zone:
        return self.__zone

    def get_color(self) -> Any:
        return self.__color

    def get_max_drones(self) -> int:
        return self.__max_drones

    def set_max_drones(self, max_drones: int) -> int:
        if (max_drones < 1):
            max_drones = 1
        self.__max_drones = max_drones

    def get_connections(self) -> list[Connection]:
        return self.__connections

    def move_to(self, drone_id: int, next_hub: "Hub") -> None:
        """Function for making the drone move to the next hub"""
        exist: bool = False
        if next_hub is self.wait():
            return
        for connection in self.get_connections():
            temp_hub: Hub = connection.other_hub(self)
            if temp_hub is next_hub:
                exist = True
        if not exist:
            if self.get_name() != "Wait" and next_hub.get_name() != "Wait":
                print(
                    "There is not a connection between "
                    f"{self.get_name()} and {next_hub.get_name()}")
            return
        for i in range(len(self.drones)):
            if self.drones[i].get_id() == drone_id:
                next_hub.drones.append(self.drones.pop(i))
                return

    @classmethod
    def wait(cls) -> "Hub":
        """Function for returning the unique wait hub for waiting"""
        if cls.wait_Hub is None:
            cls.wait_Hub = Hub("Wait", 0, 0, -1, Zone.normal,
                               max_drones=10000000)
        return cls.wait_Hub

    def add_connection(self, new_connection: Connection) -> None:
        """Function for adding a connection to a hub"""
        self.__connections.append(new_connection)

    def check_connection_exist(self, hub_1: "Hub", hub_2: "Hub") -> bool:
        """Function for verifying if a connection exist between 2 hubs"""
        for connection in self.get_connections():
            if ((connection.get_edge_1() == hub_1
                 and connection.get_edge_2() == hub_2)
                or (connection.get_edge_1() == hub_2
                    and connection.get_edge_2() == hub_1)):
                return True
        return False

    def calculate_hub_cost(self) -> int:
        """Function for calculating the cost for moving to a hub"""
        if self.get_zone().name == "normal":
            return 1
        elif self.get_zone().name == "blocked":
            return -1
        elif self.get_zone().name == "restricted":
            return 2
        elif self.get_zone().name == "priority":
            return 1
        return 0

    def check_hub_contraint(self, drone: "Hub.Drone", f: int,
                            constraints: list[Constraint]) -> bool:
        """Function for checking a hub based on the constraints

        this function checks the constraints list, looking for a collision
        between de actual time and drone and the same time and drone at the
        list, if the function detects a collision return true, if it doesn't
        it return false.

        It also checks the f + 1, in the case the reach_zone is restricted.

        Args:
            drone (Hub.Drone): the drone being checked
            constraints (list[tuple]): the list with the constraints of the
                possible solution

        Returns:
            bool: a boolean for the constraints check result
        """
        for constraint in constraints:
            if isinstance(constraint[1], str):
                if (constraint[0] == drone
                        and constraint[1] == self.get_name()
                        and constraint[2] == f):
                    return True
                if (self.get_zone().value == "restricted"):
                    if (constraint[0] == drone
                            and constraint[1] == self.get_name()
                            and constraint[2] == f + 1):
                        return True
        return False

    def get_lowest_neighbor(self, possible_hubs:
                            list[tuple["Hub", Connection]],
                            last_hub: "Hub") -> tuple["Hub", Connection] | bool:
        """Function for deciding the lowest neighbor to move to"""
        priority_list: list[tuple["Hub", Connection]] = []
        result: tuple["Hub", Connection]

        if len(possible_hubs) == 0:
            return (self, Connection.wait())
        for hub, connection in possible_hubs:
            if hub.get_zone() == Zone.priority:
                priority_list.append((hub, connection))
        if len(priority_list) > 0:
            result = priority_list[0]
        else:
            result = possible_hubs[0]
        if (result[0] == last_hub):
            exit(1)
            return True
        else:
            return result

    def calculate_route(
            self, drone: "Hub.Drone", heuristic: dict[str, int],
            constraints: list[Constraint]) -> list[Checkpoint]:
        """Function for calculating the route for a drone

        This function tries to get the drone from the start hub to the end hub,
        taking in to account the constraints.

        It only moves to another hub if that moves have same or lower cost.

        If there are no possible lower neighbors, it just wait a turn.

        Args:
            drone (Hub.Drone): the specific drone for which the route is
                gonna be calculated
            heuristic (dict[str, int]): the dictionary with the specific
                heuristic of each hub
            constraints (list[Constraints]): the list of constraints

        Returns:
            list[Checkpoint]: the final pathing of the drone
        """
        g: int = 1
        actual_hub: Hub = self
        route: list[Checkpoint] = []
        last_hub: str = actual_hub.get_name()
        temp_checkpoint: tuple["Hub", Connection] | bool
        next_connection: Connection

        while actual_hub.get_type_of_hub() != 2:
            actual_cost = heuristic.get(actual_hub.get_name(), 10000) + g
            t = actual_cost
            posibble_hubs: list[tuple[Hub, Connection]] = []

            for connection in actual_hub.get_connections():
                temp_hub = connection.other_hub(actual_hub)
                f = heuristic.get(temp_hub.get_name(), 10000) + g
                if f <= t:
                    if (
                        temp_hub.check_hub_contraint(drone, g, constraints)
                            or connection.check_connection_constraint(
                                drone, g, constraints, temp_hub.get_zone())):
                        continue
                    if (f < t):
                        posibble_hubs = [(temp_hub, connection)]
                        t = f
                    else:
                        posibble_hubs.append((temp_hub, connection))

            temp_checkpoint = actual_hub.get_lowest_neighbor(
                posibble_hubs, last_hub)
            gap: int = 1
            while (isinstance(temp_checkpoint, bool)):
                posibble_hubs: list[tuple[Hub, Connection]] = []

                for connection in actual_hub.get_connections():
                    temp_hub = connection.other_hub(actual_hub)
                    f = heuristic.get(temp_hub.get_name(), 10000) + g
                    if f <= t + gap:
                        if (
                            temp_hub.check_hub_contraint(drone, g, constraints)
                                or connection.check_connection_constraint(
                                    drone, g, constraints, temp_hub.get_zone())):
                            continue
                        posibble_hubs.append((temp_hub, connection))
                posibble_hubs = [t for t in posibble_hubs
                                 if t[0].get_name() != last_hub]
                temp_checkpoint = actual_hub.get_lowest_neighbor(
                    posibble_hubs, last_hub)
                gap += 1
            last_hub = actual_hub.get_name()
            actual_hub, next_connection = temp_checkpoint

            route.append((actual_hub.get_name(), g, next_connection))
            if (next_connection is Connection.wait()):
                g += 1
            else:
                g += actual_hub.calculate_hub_cost()

        return route

    def create_drones(self, nb_drones: int) -> None:
        """Function for creating drones at the start hub"""
        if self.get_type_of_hub() != 1:
            print("Only the start_hub can create drones")
        else:
            for i in range(nb_drones):
                drone: Hub.Drone = self.Drone(i)
                self.drones.append(drone)

    def __str__(self) -> str:
        result: str
        result = (f"Name: {self.get_name()}, [{self.get_x()}, "
                  f"{self.get_y()}], zone: {self.get_zone()}, "
                  f"color: {self.get_color()}, "
                  f"max drones: {self.get_max_drones()}")
        if len(self.get_connections()) == 0:
            return result
        result += "\nConnections:\n"
        for connection in self.get_connections():
            result += "- " + connection.__str__() + "\n"
        return result

    def __repr__(self) -> str:
        return self.__str__()
