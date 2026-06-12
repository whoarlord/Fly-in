from typing import Optional
from Hub import Hub, Connection
from CT import CT, Conflict, Solution, Constraint

Ocuppied = dict[tuple[str | Connection, int], tuple[list[Hub.Drone], int]]


class Map:
    """A class representing a map for the drones

    Attributes:
        __map (Optional[Map]): the variable representing the unique map
        nb_drones (int): the number of drone to be created
        end_hub (Hub): the hub where the drones have to finish
        heuristic (dict[str, int]): a dictionary for the
            heuristic value of each hub
        constraint_tree (CT): the constraint tree for the cbs algorithm
        hubs (set[Hub]): the set of hubs received
    """
    __map: Optional["Map"] = None
    nb_drones: int = -1
    start_hub: Hub
    end_hub: Hub
    heuristic: dict[str, int] = {}
    constraint_tree: CT = CT([], [])
    hubs: set[Hub] = set()

    def __new__(cls) -> "Map":
        """Method for returning the unique drone_map"""
        if cls.__map is None:
            cls.__map = object.__new__(cls)
        return cls.__map

    def get_hub(self, hub_str: str) -> Hub:
        """It receives a name and returns the hub corresponding to that name"""
        for hub in self.hubs:
            if hub.get_name() == hub_str:
                return hub
        return Hub.wait()

    def update_drones(self, nb_drones: int) -> None:
        """function for initializing the number of drones"""
        self.nb_drones = nb_drones

    def add_hub(self, new_hub: Hub) -> None:
        """Function for adding a hub

        This function checks if the name or coordinates of the hub
        are already in the map, and add them if all is correct

        Args:
            new_hub (Hub): the hub to add
        """
        for hub in self.hubs:
            if new_hub.get_name() == hub.get_name():
                raise ValueError("Duplicated name of hubs")
            elif new_hub.get_x() == hub.get_x() and new_hub.get_y() == hub.get_y():
                raise ValueError("Duplicated coordinates for hubs")
        self.hubs.add(new_hub)
        if new_hub.get_type_of_hub() == 1:
            self.start_hub = new_hub
        elif new_hub.get_type_of_hub() == 2:
            self.end_hub = new_hub

    def create_connection(
            self, edge_1: str, edge_2: str, max_link_capacity: int) -> bool:
        """Function for creating the connection between two hubs

        This function checks if both hubs exist and aren't the same
        . then it checks if the connection already exists and finally
        if all goes fine, it creates the connection

        Args:
            edge_1 (str): name of the first edge_hub
            edge_2 (str): name of the second edge_hub
            max_link_capcity (int): the maximum capacity of the link

        Returns:
            bool: returns true if there was an error and false if it doesn't
        """
        connection_1: int = 0
        connection_2: int = 0
        hub_1: Hub
        hub_2: Hub
        connection: Connection
        for hub in self.hubs:
            if hub.get_name() == edge_1:
                hub_1 = hub
                connection_1 = 1
            elif hub.get_name() == edge_2:
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
        """Function for checking if there is a start and a end hub"""
        start: int = 0
        end: int = 0
        for hub in self.hubs:
            if hub.get_type_of_hub() == 1:
                hub.set_max_drones(self.nb_drones)
                start += 1
            elif hub.get_type_of_hub() == 2:
                hub.set_max_drones(self.nb_drones)
                end += 1
        if start == 0:
            raise ValueError("No start hub where gave")
        elif end == 0:
            raise ValueError("No end hub where gave")
        elif end == 0 and start == 0:
            raise ValueError("No start and end hub where gave")

    def initialize_drones(self) -> None:
        """Function for initializing all the drones at the start hub"""
        for hub in self.hubs:
            if hub.get_type_of_hub() == 1:
                hub.create_drones(self.nb_drones)
                print("drones Created")
                return
        raise ValueError("we cant create the drones")

    def normalize_coordinates(self) -> None:
        """Function for making all the coordinates positive"""
        lwr_x: int = 0
        lwr_y: int = 0
        for hub in self.hubs:
            if hub.get_x() < lwr_x:
                lwr_x = hub.get_x()
            if hub.get_y() < lwr_y:
                lwr_y = hub.get_y()
        lwr_x = lwr_x * -1
        lwr_y = lwr_y * -1
        if lwr_x > 0 or lwr_y > 0:
            for hub in self.hubs:
                hub.add_x(lwr_x)
                hub.add_y(lwr_y)

    def check_conflicts(self) -> Optional[Conflict]:
        """Function for checking conflicts between drone solutions

        This function iterates over the solutions and save the position
        where the drone is at the specific time, so if two drones are
        at the same time in the same hub, it creates a conflict if there are
        more drones that the hub can retain

        Then it does the same for the connections

        Returns:
            Optional[Conflict]: it returns a tuple with the time, the hub or
                the connecion, and the drones in conflict
        """
        ocuppied: Ocuppied = {}
        for drone_id, path in self.constraint_tree.solutions:
            for checkpoint in path:
                position, t, connection = checkpoint
                hub = self.get_hub(position)

                conflict = self.register_state_hub(
                    position, t, ocuppied, drone_id, hub, False)
                if (conflict is not None):
                    return conflict

                if hub.get_zone().value == 'restricted':
                    already_in_path = any(
                        p == position and ts == t + 1
                        for p, ts, _ in path
                    )
                    if not already_in_path:
                        conflict = self.register_state_hub(
                            position, t + 1, ocuppied, drone_id, hub, True)
                        if conflict is not None:
                            return conflict

        ocuppied = {}
        for drone_id, path in self.constraint_tree.solutions:
            for checkpoint in path:
                position, t, connection = checkpoint
                hub = self.get_hub(position)

                conflict = self.register_state_connection(
                    connection, t, ocuppied, drone_id, False)
                if (conflict is not None):
                    return conflict

                if hub.get_zone().value == 'restricted':
                    already_in_path = any(
                        p == position and ts == t + 1
                        for p, ts, _ in path
                    )
                    if not already_in_path:
                        conflict = self.register_state_connection(
                            connection, t + 1, ocuppied, drone_id, True)
                        if conflict is not None:
                            return conflict
        return None

    def register_state_connection(
            self, connection: Connection, t: int, ocuppied: Ocuppied,
            drone_id: Hub.Drone, restricted: bool) -> Optional[Conflict]:
        """Function for registering the connection at the ocuppied dict

        This function updates the ocuppied dictionary with the drone ids,
        and the time whem that drones reach the hub

        But if it detects a conflict it returns it

        Returns:
            Optional[Conflict]: it returns a tuple with the time, the hub or
                the connecion, and the drones in conflict
        """
        key = connection, t
        ids, count = ocuppied.get(key, ([], 0))

        count += 1
        ids = ids + [drone_id]

        if count > connection.max_link_capacity:
            if (restricted):
                t -= 1
            return Conflict({
                "v": connection,
                "t": t,
                "drones": [ids[-2], drone_id]
            })

        ocuppied[key] = (ids, count)
        return None

    def register_state_hub(
            self, position: str | Connection, t: int, ocuppied: Ocuppied,
            drone_id: Hub.Drone, hub: Hub,
            restricted: bool) -> Optional[Conflict] | None:
        """Function for registering the connection at the ocuppied dict

        This function updates the ocuppied dictionary with the drone ids,
        and the time whem that drones reach the hub

        But if it detects a conflict it returns it

        Returns:
            Optional[Conflict]: it returns a tuple with the time, the hub or
                the connecion, and the drones in conflict
        """
        key = position, t
        ids, count = ocuppied.get(key, ([], 0))

        count += 1
        ids = ids + [drone_id]

        if count > hub.get_max_drones():
            if (restricted):
                t -= 1
            return Conflict({
                "v": position,
                "t": t,
                "drones": [ids[-2], drone_id]
            })

        ocuppied[key] = (ids, count)
        return None

    def update_heuristic(
            self, hub: Hub, cost: int, restricted: bool = False) -> None:
        """Function for calculating the heuristic of each hub

        This function calculates the cost to reach from the specific
        hub to the final hub.

        For that it starts at the end hub, and expands it with a recursive
        calling until reaching the start hub or a blocked hub

        Args:
            hub (Hub): the actual hub where we are at
            cost (int): the cost calculated until actual hub
            restricted (bool): the bool specifying if the actuak hub is
                restricted or not
        """

        current = self.heuristic.get(hub.get_name())

        if current is not None and current <= cost:
            return

        self.heuristic[hub.get_name()] = cost

        for connection in hub.get_connections():
            next_hub = connection.other_hub(hub)

            hub_cost = next_hub.calculate_hub_cost()

            if hub_cost == -1:
                continue

            self.update_heuristic(
                next_hub,
                cost + hub_cost
            )

    def is_connected(self) -> bool:
        """This function checks if all the hubs are connected

        This functions makes a dfs search from 1 have to all the others
        and if the len of the visited hubs is the same that the len
        of all the hubs, it returns true, in the other case it returns false

        Returns:
            bool: it returns true if all the map is connected and false in the
                other case
        """
        visited = set()

        def dfs(hub: Hub) -> None:
            """Function for checking the connection"""
            visited.add(hub.get_name())

            for connection in hub.get_connections():
                next_hub = connection.other_hub(hub)

                if next_hub.get_name() not in visited:
                    dfs(next_hub)

        dfs(list(self.hubs)[0])

        return len(visited) == len(self.hubs)

    def update_affected_solution(self, affected_drone: Hub.Drone,
                                 constraints: list[Constraint],
                                 current_solution: list[Solution]
                                 ) -> list[Solution]:
        """Function for updating only the conflicting drone

        This function update the soltion of the drone that needs
        to change because of the conflict created

        Args:
            affected_drone (Hub.Drone): the affected drone
            constraints (list[Constraints]): the list of constraints
            current_solution (list[Solution]): the list of solutions
                before the change

        Returns:
            list[Solution]: the list of the solutions with the updated
                solution for the affected drone
        """

        solutions: list[Solution] = []
        for drone, path in current_solution:
            if (drone.get_id() == affected_drone.get_id()):
                solution = self.start_hub.calculate_route(
                    drone, self.heuristic, constraints)
                solutions.append((drone, solution))
            else:
                solutions.append((drone, path))
        return solutions

    def update_solutions(
            self, constraints: list[Constraint]) -> list[Solution]:
        """Function for updating only the conflicting drone

        This function calculates the solution for all the drones
        at the first time

        Args:
            constraints (list[Constraints]): the list of constraints

        Returns:
            list[Solution]: the list of the solutions for all the drones
        """
        solutions: list[Solution] = []
        for drone in self.start_hub.drones:
            solution = self.start_hub.calculate_route(
                drone, self.heuristic, constraints)
            solutions.append((drone, solution))
        return solutions

    def initialize_heuristic_and_routes(self) -> None:
        """Initialize the heuristic and the routes for the drones"""
        if (self.is_connected() is False):
            print("No estan todos los hubs conectados")
            exit(1)
        self.update_heuristic(self.end_hub, 0)
        if (self.heuristic.get(self.start_hub.get_name()) is None):
            print("is imposible to go to the end from the entry")
            exit(1)
        solutions = self.update_solutions(self.constraint_tree.constraints)
        self.constraint_tree = CT([], solutions)

    def solve(self) -> None:
        """Main function for initializing, resolving and visualizing"""
        from Graphics import Graphics

        try:
            self.initialize_heuristic_and_routes()
            print(f"heuristic: {self.heuristic}")
            self.cbs()
        except KeyboardInterrupt:
            print("interrupted")
        print(self.constraint_tree.solutions)
        g: Graphics = Graphics()
        g.initialize_graphics(self)

    def cbs(self) -> None:
        """The main loop for solving the problem with conflicts

        This function checks the conflicts between the posible solution
        of each drone, and if it detects any conflict it generate two possible
        solutions, saves the worst at checkpoints and continue expanding from
        the other solution, if it gets worst than the checkpoint it starts
        backtracking
        """
        max_iter = 2000

        for i in range(max_iter):
            conflict = self.check_conflicts()
            if conflict is None:
                break
            print(f"conflict: {conflict}")

            self.constraint_tree.create_new_tree(
                conflict, self, self.constraint_tree.solutions)

    def __str__(self) -> str:
        result: str = ""
        for hub in self.hubs:
            result += hub.__str__() + "\n"
        return result
