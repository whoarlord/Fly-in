from Map import Map
from Parser import Parser
import sys


def main() -> None:
    if len(sys.argv) != 2:
        print("Invalid number of arguments")
        return
    drone_map: Map = Map()
    file_name: str = sys.argv[1]
    parser: Parser = Parser()
    parser.initialize(drone_map, file_name)
    print(drone_map)
    try:
        drone_map.initialize_drones()
    except ValueError as e:
        print(f"Error while creating drones: {e}")
        return
    drone_map.solve()


if __name__ == "__main__":
    main()
