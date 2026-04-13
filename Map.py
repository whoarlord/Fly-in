from typing import Any
from Hub import Hub, Connection


class Map:
    __map: Any = None
    __nb_drones: int
    heuristic: dict[str, int] = {}

    hubs: set[Hub] = set()

    def __new__(cls) -> Any:
        if cls.__map is None:
            cls.__map = object.__new__(cls)
        return cls.__map

    def update_drones(self, nb_drones: int) -> None:
        self.__nb_drones = nb_drones

    def add_hub(self, new_hub: Hub) -> None:
        for hub in self.hubs:
            if new_hub.name == hub.name:
                raise ValueError("Duplicated name of hubs")
            elif new_hub.x == hub.x and new_hub.y == hub.y:
                raise ValueError("Duplicated coordinates for hubs")
        self.hubs.add(new_hub)

    def get_nb_drones(self) -> int:
        return self.__nb_drones

    def create_connection(
            self, edge_1: str, edge_2: str, max_link_capacity: int) -> bool:
        connection_1: int = 0
        connection_2: int = 0
        hub_1: Hub
        hub_2: Hub
        connection: Connection
        for hub in self.hubs:
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
        for hub in self.hubs:
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
        for hub in self.hubs:
            if hub.type_of_hub == 1:
                hub.create_drones(self.__nb_drones)
                print("drones Created")
                return
        raise ValueError("we cant create the drones")

    def normalize_coordinates(self):
        lwr_x: int = 0
        lwr_y: int = 0
        for hub in self.hubs:
            if hub.x < lwr_x:
                lwr_x = hub.x
            if hub.y < lwr_y:
                lwr_y = hub.y
        lwr_x = lwr_x * -1
        lwr_y = lwr_y * -1
        if lwr_x > 0 or lwr_y > 0:
            for hub in self.hubs:
                hub.x += lwr_x
                hub.y += lwr_y

    def check_finish(self):
        for hub in self.hubs:
            if hub.type_of_hub == 2:
                if len(hub.drones) == self.__nb_drones:
                    return 0
                return 1

    def update_heuristic(self, hub: Hub, cost: int) -> None:
        self.heuristic.update({hub.name: cost})
        next_hub: Hub
        actual_cost: int
        for connection in hub.connections:
            next_hub = connection.other_hub(hub)
            actual_cost = self.heuristic.get(next_hub.name, -1)
            if actual_cost == -1 or actual_cost > cost:
                if (next_hub.calculate_hub_cost() == -1):
                    continue
                self.update_heuristic(
                    next_hub, cost + next_hub.calculate_hub_cost())

    def initialize_heuristic_and_routes(self) -> None:
        for hub in self.hubs:
            if hub.type_of_hub == 2:
                self.update_heuristic(hub, 0)
                break
        print(self.heuristic)
        for hub in self.hubs:
            if hub.type_of_hub == 1:
                for drone in hub.drones:
                    hub.calculate_route(drone, self.heuristic)
                    print(drone)

    def solve(self) -> None:
        from Graphics import Graphics

        self.initialize_heuristic_and_routes()
        # while (self.check_finish()):
        g: Graphics = Graphics()
        g.initialize_graphics(self)

    def __str__(self) -> str:
        result: str = ""
        for hub in self.hubs:
            result += hub.__str__() + "\n"
        return result
