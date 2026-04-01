from Map import Map
from Hub import Hub, Zone
from typing import Any
import sys


def create_connection(drone_map: Map, arguments: list[str], type_of_hub: int):
    pass


def create_hub(drone_map: Map, arguments: list[str], type_of_hub: int):
    metadata: list[str] = []
    attribute: list[str] = []
    zone: Zone = Zone.normal
    color: Any = None
    max_drones: int = 1
    if len(arguments) < 3:
        return 1
    elif len(arguments) > 3:
        for i in range(3, len(arguments)):
            metadata = arguments[i].split()
            for value in metadata:
                attribute = value.strip("[]")
                attribute = attribute.split("=")
                if len(attribute) != 2:
                    return 1
                elif attribute[0] == "color":
                    attribute = attribute[1].split()
                    if len(attribute) != 1:
                        return 1
                    color = attribute[0]
                elif attribute[0] == "zone":
                    zone = Zone(attribute[1])
                elif attribute[0] == "max_drones":
                    max_drones = int(attribute[1])
                else:
                    return 1
    drone_map.add_hub(Hub(arguments[0], int(arguments[1]), int(arguments[2]),
                          type_of_hub, zone, color, max_drones))
    return 0


def initialize(drone_map: Map, file_name: str) -> bool:
    i: int = 1
    line_splitted: list[str]
    arguments_splitted: list[str]
    with open(file_name) as file:
        for line in file:
            try:
                line = line.strip()
                line_splitted = line.split(":")
                if len(line) == 0:
                    i += 1
                    continue
                elif (line_splitted[0] == "nb_drones"):
                    if i == 1:
                        drone_map.update_drones(int(line_splitted[1]))
                    else:
                        print("number of drones is not at first line")
                        return True
                elif line_splitted[0] == "start_hub":
                    arguments_splitted = line_splitted[1].split()
                    if (create_hub(drone_map, arguments_splitted, 1)):
                        print("invalid arguments for hub")
                        return True
                elif line_splitted[0] == "end_hub":
                    arguments_splitted = line_splitted[1].split()
                    if (create_hub(drone_map, arguments_splitted, 2)):
                        print("invalid arguments for hub")
                        return True
                elif line_splitted[0] == "hub":
                    arguments_splitted = line_splitted[1].split()
                    if (create_hub(drone_map, arguments_splitted, 0)):
                        print("invalid arguments for hub")
                        return True
                elif line_splitted[0] == "connection":
                    arguments_splitted = line_splitted[1].split()
                    if (create_connection(drone_map, arguments_splitted, 2)):
                        print("invalid arguments for hub")
                        return True
                if line[0] == "#":
                    continue
                i += 1
            except Exception as e:
                print(f"Exception caught: {e}")
    return False


def main() -> None:
    if len(sys.argv) != 2:
        print("Invalid number of arguments")
        return
    drone_map: Map = Map()
    file_name: str = sys.argv[1]
    if initialize(drone_map, file_name):
        return
    print(drone_map)


if __name__ == "__main__":
    main()
