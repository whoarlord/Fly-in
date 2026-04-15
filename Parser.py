from Map import Map
from Hub import Hub, Zone
from typing import Any


class Parser:
    start: int = 0
    end: int = 0

    @staticmethod
    def create_connection_main(
            drone_map: Map, arguments: list[str]) -> None:
        max_link_capacity: int = 1
        line_splitted: list[str]
        line_splitted_link: list[str]
        if len(arguments) > 2:
            raise ValueError(
                "Invalid number of arguments for connections")
        elif len(arguments) <= 2 and len(arguments) > 0:
            line_splitted = arguments[0].split("-")
            if len(line_splitted) != 2:
                raise ValueError("Invalid number of edges")
            elif len(arguments) == 2:
                line_splitted_link = arguments[1][1:-1].split("=")
                if len(line_splitted_link) != 2:
                    raise ValueError(
                        "Invalid number of metadata")
                elif line_splitted_link[0] != "max_link_capacity":
                    raise ValueError("Invalid metadata key")
                max_link_capacity = int(line_splitted_link[1])
                if max_link_capacity < 0:
                    raise ValueError("max link capacity, must be positive")
            if (drone_map.create_connection(
                line_splitted[0],
                line_splitted[1],
                    max_link_capacity)):
                raise ValueError(
                    "Invalid edges for connection")

    def create_hub(self, drone_map: Map, arguments: list[str],
                   type_of_hub: int) -> None:
        metadata: list[str] = []
        attribute: list[str] = []
        zone: Zone = Zone.normal
        color: Any = None
        max_drones: int = 1
        if self.start == 1 and type_of_hub == 1:
            raise ValueError("Duplicated start hub, at line")
        elif self.end == 1 and type_of_hub == 2:
            raise ValueError("Duplicated end hub, at line")
        elif len(arguments) < 3:
            raise ValueError(
                "Invalid number of arguments for hub")
        elif len(arguments) > 3:
            for i in range(3, len(arguments)):
                metadata = arguments[i].split()
                for value in metadata:
                    if len(arguments) - 1 == 3:
                        if value[0] != "[" or value[-1] != "]":
                            raise ValueError("Invalid metadata format")
                        attribute = value[1:-1].split("=")
                    elif i == 3:
                        if value[0] != "[":
                            raise ValueError("Invalid metadata format")
                        attribute = value[1:].split("=")
                    elif i == len(arguments) - 1:
                        if value[-1] != "]":
                            raise ValueError(
                                "Invalid metadata format")
                        attribute = value[:-1].split("=")
                    else:
                        attribute = value.split("=")
                    if len(attribute) != 2:
                        raise ValueError("invalid number of key/value "
                                         "for hub")
                    elif attribute[0] == "color":
                        color = attribute[1]
                    elif attribute[0] == "zone":
                        zone = Zone(attribute[1])
                    elif attribute[0] == "max_drones":
                        max_drones = int(attribute[1])
                        if max_drones < 0:
                            raise ValueError(
                                "Invalid max_drones limit, "
                                "must be positive")
                    else:
                        raise ValueError(
                            "Invalid metadata key")

        if type_of_hub == 1:
            self.start = 1
        elif type_of_hub == 2:
            self.end = 1
        drone_map.add_hub(Hub(arguments[0], int(arguments[1]), int(
            arguments[2]), type_of_hub, zone, color, max_drones))

    def initialize(self, drone_map: Map, file_name: str) -> None:
        i: int = 1
        nb_drones: bool = False
        line_splitted: list[str]
        arguments_splitted: list[str]
        try:
            with open(file_name) as file:
                for line in file:
                    line = line.strip()
                    line_splitted = line.split(":")
                    if len(line) == 0 or line[0] == "#":
                        i += 1
                        continue
                    elif (line_splitted[0] == "nb_drones"):
                        if nb_drones is False:
                            nb_drones: int = int(line_splitted[1])
                            if nb_drones < 0:
                                raise ValueError(
                                    "Number of drones must be negative")
                            drone_map.update_drones(nb_drones)
                        else:
                            raise ValueError("number of drones is not "
                                             "at first line")
                    elif line_splitted[0] == "start_hub":
                        arguments_splitted = line_splitted[1].split()
                        self.create_hub(drone_map, arguments_splitted, 1)
                    elif line_splitted[0] == "end_hub":
                        arguments_splitted = line_splitted[1].split()
                        self.create_hub(drone_map, arguments_splitted, 2)
                    elif line_splitted[0] == "hub":
                        arguments_splitted = line_splitted[1].split()
                        self.create_hub(drone_map, arguments_splitted, 0)
                    elif line_splitted[0] == "connection":
                        arguments_splitted = line_splitted[1].split()
                        self.create_connection_main(
                            drone_map, arguments_splitted)
                    i += 1
                    nb_drones = True
            drone_map.check_start_end()
            drone_map.normalize_coordinates()
        except ValueError as e:
            print(f"{e}, at line {i}")
            exit(1)
