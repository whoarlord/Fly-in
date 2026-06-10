from Map import Map
from Parser import Parser
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Invalid number of arguments")
        exit(1)
    drone_map: Map = Map()
    file_name: str = sys.argv[1]
    parser: Parser = Parser()
    try:
        parser.initialize(drone_map, file_name)
        if (drone_map.nb_drones == -1):
            raise ValueError("There weren't specified the drones")
        drone_map.initialize_drones()
    except ValueError as e:
        print(f"Error while creating drones: {e}")
        exit(1)
    except PermissionError as e:
        print(e)
        exit(1)
    print(drone_map)
    drone_map.solve()


if __name__ == "__main__":
    main()
