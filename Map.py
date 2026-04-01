from typing import Any
from Hub import Hub


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

    def __str__(self):
        result: str = ""
        for hub in self.__hubs:
            result += hub.__str__() + "\n"
        return result
