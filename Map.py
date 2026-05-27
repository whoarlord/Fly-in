from typing import Any
from Hub import Hub, Connection
from CT import CT
import heapq


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
        for hub in self.hubs:
            if hub.name == hub_str:
                return hub
        return Hub.wait()

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
                hub.max_drones = self.nb_drones
                start += 1
            elif hub.type_of_hub == 2:
                hub.max_drones = self.nb_drones
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

    def normalize_coordinates(self) -> None:
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

    def check_conflicts(self) -> dict | None:
        ocuppied: dict[tuple, tuple[list, int]] = {}
        for drone_id, path in self.constraint_tree.solutions:
            for checkpoint in path:
                position, t, connection = checkpoint
                hub = self.get_hub(position)

                conflict = self.register_state_hub(
                    position, t, ocuppied, drone_id, hub)
                if (conflict is not None):
                    return conflict

                if hub.zone.value == 'restricted':
                    conflict = self.register_state_hub(
                        position, t + 1, ocuppied, drone_id, hub)
                    if (conflict is not None):
                        return conflict

        ocuppied = {}
        for drone_id, path in self.constraint_tree.solutions:
            for checkpoint in path:
                position, t, connection = checkpoint
                hub = self.get_hub(position)

                conflict = self.register_state_connection(
                    connection, t, ocuppied, drone_id, hub)
                if (conflict is not None):
                    return conflict

                if hub.zone.value == 'restricted':
                    conflict = self.register_state_connection(
                        connection, t + 1, ocuppied, drone_id, hub)
                    if (conflict is not None):
                        return conflict
        return None

    def register_state_connection(
            self, connection: Connection, t: int, ocuppied: dict,
            drone_id: int, hub: Hub) -> dict:
        key = connection, t
        ids, count = ocuppied.get(key, ([], 0))

        count += 1
        ids = ids + [drone_id]

        if count > connection.max_link_capacity:
            return {
                "v": connection,
                "t": t,
                "drones": [ids[-2], drone_id]
            }

        ocuppied[key] = (ids, count)
        return None

    def register_state_hub(
            self, position: str | Connection, t: int, ocuppied: dict,
            drone_id: int, hub: Hub) -> dict | None:

        key = position, t
        ids, count = ocuppied.get(key, ([], 0))

        count += 1
        ids = ids + [drone_id]

        if count > hub.max_drones:
            return {
                "v": position,
                "t": t,
                "drones": [ids[-2], drone_id]
            }

        ocuppied[key] = (ids, count)
        return None

    def update_heuristic(
            self, hub: Hub, cost: int, restricted: bool = False) -> None:
        self.heuristic.update({hub.name: cost})
        next_hub: Hub
        actual_cost: int
        for connection in hub.connections:
            next_hub = connection.other_hub(hub)
            actual_cost = self.heuristic.get(next_hub.name, -1)
            if actual_cost == -1 or actual_cost > cost:
                if (next_hub.calculate_hub_cost() == -1):
                    continue
                if (restricted):
                    if (self.heuristic.get(next_hub.name, -1) == 2):
                        self.update_heuristic(
                            next_hub, cost + 2, True)
                    else:
                        self.update_heuristic(
                            next_hub, cost + 2, False)
                else:
                    if (self.heuristic.get(next_hub.name, -1) == 2):
                        self.update_heuristic(
                            next_hub, cost + 1, True)
                    else:
                        self.update_heuristic(
                            next_hub, cost + 1, False)

    def create_solution(
            self, drone: Hub.Drone, constraints: list[tuple]) -> list[tuple]:
        return self.start_hub.calculate_route(
            drone, self.heuristic,
            constraints, self)

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
        # try:
        #     finish = self.cbs_greedy()
        # except KeyboardInterrupt:
        #     print("finish: ")
        conflict: Any = {}
        try:
            while (conflict is not None):
                conflict = self.check_conflicts()
                if conflict is None:
                    break
                self.constraint_tree.create_new_tree(conflict, self)
        except KeyboardInterrupt:
            print("close")
        print(self.constraint_tree.constraints)
        g: Graphics = Graphics()
        g.initialize_graphics(self)

    def cbs_greedy(
            self, constraints: list = None, depth: int = 0, beam: list = []) -> bool:
        """
        Greedy DFS: en cada nivel elige la rama de menor costo.
        Si se atasca, hace backtracking al beam guardado.
        """

        # Después del heappush, podar si crece demasiado
        if len(beam) > 3:
            # Quedarse solo con los MAX_BEAM mejores
            beam_sorted = sorted(beam)[:5]
            beam.clear()
            beam.extend(beam_sorted)
            heapq.heapify(beam)
        if constraints is None:
            constraints = self.constraint_tree.constraints.copy()

        solutions = self.update_solutions(constraints)
        cost = self.constraint_tree.calculate_cost(solutions)
        self.constraint_tree.re_define_values(constraints, solutions, cost)

        conflict = self.check_conflicts()
        if conflict is None:
            return True
        print(conflict)

        # Generar las dos ramas
        candidates = []
        for drone in conflict["drones"]:
            new_constraints = constraints.copy()
            new_constraint = (drone, conflict["v"], conflict["t"])
            new_constraints.append(new_constraint)
            branch_solutions = self.update_solutions(new_constraints)
            branch_cost = self.constraint_tree.calculate_cost(branch_solutions)
            candidates.append((branch_cost, new_constraints))

        if not candidates:
            return False

        # Ordenar: mejor costo primero
        candidates.sort(key=lambda x: x[0])
        best_cost, best_constraints = candidates[0]

        # Guardar la rama alternativa en el beam (backtracking point)
        if len(candidates) > 1:
            fallback_cost, fallback_constraints = candidates[1]
            heapq.heappush(beam, (fallback_cost, id(
                fallback_constraints), fallback_constraints))

        # Explorar la mejor rama
        if self.cbs_greedy(best_constraints, depth + 1, beam):
            return True

        # ── BACKTRACKING: la mejor rama falló, probar desde el beam ──
        print(f"[backtrack] depth={depth}, beam_size={len(beam)}")
        while beam:
            _, _, fallback_constraints = heapq.heappop(beam)
            if self.cbs_greedy(
                    fallback_constraints, depth + 1, beam):
                return True
            print(beam)

        return False

    def __str__(self) -> str:
        result: str = ""
        for hub in self.hubs:
            result += hub.__str__() + "\n"
        return result
