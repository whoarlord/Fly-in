from Map import Map
from Hub import Hub, Zone
from typing import Any


class Parser:
    start: int = 0
    end: int = 0

    @staticmethod
    def create_connection_main(
            drone_map: Map, arguments: list[str],
            line: int) -> None:
        max_link_capacity: int = 1
        line_splitted: list[str]
        line_splitted_link: list[str]
        if len(arguments) > 2:
            raise ValueError(
                f"Invalid number of arguments for connections, at line {line}")
        elif len(arguments) <= 2 and len(arguments) > 0:
            line_splitted = arguments[0].split("-")
            if len(line_splitted) != 2:
                raise ValueError(f"Invalid number of edges, at line {line}")
            elif len(arguments) == 2:
                line_splitted_link = arguments[1][1:-1].split("=")
                if len(line_splitted_link) != 2:
                    raise ValueError(
                        f"Invalid number of metadata, at line {line}")
                elif line_splitted_link[0] != "max_link_capacity":
                    raise ValueError(f"Invalid metadata key, at line {line}")
                max_link_capacity = int(line_splitted_link[1])
            if (drone_map.create_connection(
                line_splitted[0],
                line_splitted[1],
                    max_link_capacity)):
                raise ValueError(
                    f"Invalid edges for connection, at line {line}")

    def create_hub(self, drone_map: Map, arguments: list[str],
                   type_of_hub: int, line: int) -> None:
        metadata: list[str] = []
        attribute: list[str] = []
        zone: Zone = Zone.normal
        color: Any = None
        max_drones: int = 1
        if self.start == 1 and type_of_hub == 1:
            raise ValueError(f"Duplicated start hub, at line {line}")
        elif self.end == 1 and type_of_hub == 2:
            raise ValueError(f"Duplicated end hub, at line {line}")
        elif len(arguments) < 3:
            raise ValueError(
                f"Invalid number of arguments for hub, at line {line}")
        elif len(arguments) > 3:
            for i in range(3, len(arguments)):
                metadata = arguments[i].split()
                for value in metadata:
                    if len(arguments) - 1 == 3:
                        if value[0] != "[" or value[-1] != "]":
                            raise ValueError(
                                f"Invalid metadata format, at line {line}")
                        attribute = value[1:-1].split("=")
                    elif i == 3:
                        if value[0] != "[":
                            raise ValueError(
                                f"Invalid metadata format, at line {line}")
                        attribute = value[1:].split("=")
                    elif i == len(arguments) - 1:
                        if value[-1] != "]":
                            raise ValueError(
                                f"Invalid metadata format, at line {line}")
                        attribute = value[:-1].split("=")
                    else:
                        attribute = value.split("=")
                    if len(attribute) != 2:
                        raise ValueError("invalid number of key/value "
                                         f"for hub, at line {line}")
                    elif attribute[0] == "color":
                        color = attribute[0]
                    elif attribute[0] == "zone":
                        zone = Zone(attribute[1])
                    elif attribute[0] == "max_drones":
                        max_drones = int(attribute[1])
                        if max_drones < 0:
                            raise ValueError(
                                "Invalid max_drones limit, "
                                f"must be positive, at line {line}")
                    else:
                        raise ValueError(
                            f"Invalid metadata key at line {line}")
        drone_map.add_hub(Hub(arguments[0], int(arguments[1]), int(
            arguments[2]), type_of_hub, zone, color, max_drones))
        if type_of_hub == 1:
            self.start = 1
        elif type_of_hub == 2:
            self.end = 1

    def initialize(self, drone_map: Map, file_name: str) -> None:
        i: int = 1
        line_splitted: list[str]
        arguments_splitted: list[str]
        with open(file_name) as file:
            for line in file:
                line = line.strip()
                line_splitted = line.split(":")
                if len(line) == 0 or line[0] == "#":
                    i += 1
                    continue
                elif (line_splitted[0] == "nb_drones"):
                    if i == 1:
                        nb_drones: int = int(line_splitted[1])
                        if nb_drones < 0:
                            raise ValueError(
                                "Number of drones must be negative,"
                                f" at line {i} ")
                        drone_map.update_drones(nb_drones)
                    else:
                        raise ValueError("number of drones is not "
                                         f"at first line, at line {i}")
                elif line_splitted[0] == "start_hub":
                    arguments_splitted = line_splitted[1].split()
                    self.create_hub(drone_map, arguments_splitted, 1, i)
                elif line_splitted[0] == "end_hub":
                    arguments_splitted = line_splitted[1].split()
                    self.create_hub(drone_map, arguments_splitted, 2, i)
                elif line_splitted[0] == "hub":
                    arguments_splitted = line_splitted[1].split()
                    self.create_hub(drone_map, arguments_splitted, 0, i)
                elif line_splitted[0] == "connection":
                    arguments_splitted = line_splitted[1].split()
                    self.create_connection_main(
                        drone_map, arguments_splitted, i)
                i += 1
        drone_map.check_start_end()
