from typing import Any
from Hub import Hub, Connection


class Map:
    __map: Any = None
    __nb_drones: int
    __hubs: set[Hub] = set()

    def __new__(cls) -> Any:
        if cls.__map is None:
            cls.__map = object.__new__(cls)
        return cls.__map

    def update_drones(self, nb_drones: int) -> None:
        self.__nb_drones = nb_drones

    def add_hub(self, new_hub: Hub) -> None:
        self.__hubs.add(new_hub)

    def get_nb_drones(self) -> int:
        return self.__nb_drones

    def create_connection(
            self, edge_1: str, edge_2: str, max_link_capacity: int) -> bool:
        connection_1: int = 0
        connection_2: int = 0
        hub_1: Hub
        hub_2: Hub
        connection: Connection
        for hub in self.__hubs:
            if hub.name == edge_1:
                hub_1 = hub
                connection_1 = 1
            elif hub.name == edge_2:
                hub_2 = hub
                connection_2 = 1
        if not connection_1 or not connection_2:
            return True
        else:
            if (hub_1.check_connection_exist(hub_1, hub_2)):
                return True
            connection = Connection(hub_1, hub_2, max_link_capacity)
            hub_1.add_connection(connection)
            hub_2.add_connection(connection)
        return False

    def check_start_end(self) -> None:
        start: int = 0
        end: int = 0
        for hub in self.__hubs:
            if hub.type_of_hub == 1:
                start += 1
            elif hub.type_of_hub == 2:
                end += 1
        if start == 0:
            raise ValueError("No start hub where gave")
        elif end == 0:
            raise ValueError("No end hub where gave")
        elif end == 0 and start == 0:
            raise ValueError("No start and end hub where gave")

    def initialize_drones(self) -> None:
        for hub in self.__hubs:
            if hub.type_of_hub == 1:
                hub.create_drones(self.__nb_drones)
                print("drones Created")
                return
        raise ValueError("we cant create the drones")

    def __str__(self):
        result: str = ""
        for hub in self.__hubs:
            result += hub.__str__() + "\n"
        return result
