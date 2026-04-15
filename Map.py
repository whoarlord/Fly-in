from typing import Any
from Hub import Hub, Connection
from CT import CT, Conflict_types


class Map:
    __map: Any = None
    nb_drones: int
    start_hub: Hub
    end_hub: Hub
    heuristic: dict[str, int] = {}
    constraint_tree: CT = CT([], [])
    hubs: set[Hub] = set()

    def __new__(cls) -> Any:
        if cls.__map is None:
            cls.__map = object.__new__(cls)
        return cls.__map

    def get_hub(self, hub_str: str) -> Hub:
        print(hub_str)
        for hub in self.hubs:
            if hub.name == hub_str:
                return hub
        return None

    def update_drones(self, nb_drones: int) -> None:
        self.nb_drones = nb_drones

    def add_hub(self, new_hub: Hub) -> None:
        for hub in self.hubs:
            if new_hub.name == hub.name:
                raise ValueError("Duplicated name of hubs")
            elif new_hub.x == hub.x and new_hub.y == hub.y:
                raise ValueError("Duplicated coordinates for hubs")
        self.hubs.add(new_hub)
        if new_hub.type_of_hub == 1:
            self.start_hub = new_hub
        elif new_hub.type_of_hub == 2:
            self.end_hub = new_hub

    def get_nb_drones(self) -> int:
        return self.nb_drones

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
                hub.create_drones(self.nb_drones)
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

    def check_conflicts(self) -> Any:
        ocuppied: dict = {}
        for id, path in self.constraint_tree.solutions:
            for checkpoint in path:
                position, t, *_ = checkpoint
                key = position, t
                ids: list = []
                times: int = 1
                if key in ocuppied:
                    value = ocuppied[key]
                    ids.extend(value[0])
                    times = value[1]
                    conflicting_hub: Hub = self.get_hub(position)
                    times += 1
                    if times > conflicting_hub.max_drones:
                        return {
                            "type": Conflict_types.hub,
                            "v": position,
                            "t": t,
                            "drones": [ocuppied[key][0][-1], id]
                        }
                ids.append(id)
                ocuppied.update({key: [ids, times]})

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

    def create_solution(
            self, drone: Hub.Drone, constraints: list[tuple]) -> list[tuple]:
        return self.start_hub.calculate_route(
            drone, self.heuristic,
            constraints)

    def update_solutions(self, constraints: list[tuple]) -> list:
        solutions: list = []
        for drone in self.start_hub.drones:
            solutions.append([
                drone, self.create_solution(
                    drone, constraints)])
        return solutions

    def initialize_heuristic_and_routes(self) -> None:
        self.update_heuristic(self.end_hub, 0)
        solutions = self.update_solutions(self.constraint_tree.constraints)
        self.constraint_tree = CT([], solutions)

    def solve(self) -> None:
        from Graphics import Graphics

        self.initialize_heuristic_and_routes()
        conflict: Any = {}
        while (conflict is not None):
            conflict = self.check_conflicts()
            if conflict is None:
                break
            self.constraint_tree.create_new_tree(conflict, self)
        print(self.constraint_tree)
        g: Graphics = Graphics()
        g.initialize_graphics(self)

    def __str__(self) -> str:
        result: str = ""
        for hub in self.hubs:
            result += hub.__str__() + "\n"
        return result
