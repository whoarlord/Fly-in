from typing import Any
from Hub import Hub


class CT:
    """Class for describing a Constraint Tree

    Attributes:
    - constraints (list[tuple]): a list of constraints with the next structure
        (drone, hub/connection, time)
    - solutions (list): a list of specific solution routes for each drone
    - cost (int): the total cost of this solution
    - left_node (CT): a new child generated because of the conflicts between
        drones
    - rigth_node (CT): the other child
    """

    def __init__(self, constraints: list[tuple], solutions: list):
        self.constraints: list[tuple] = constraints
        self.solutions: list = solutions
        self.solutions.sort(key=lambda x: x[0].get_id(), reverse=True)
        self.cost: int = self.calculate_cost(solutions)

    def create_new_tree(self, conflict: dict, drone_map: Any):
        """Creation of new posible results based on the conflict

        Args:
        - conflict: the conflict between 2 drones in a specific time on a dict
                {type, vertex/connection, time, drones in conflict}
        - solutions: the list of the last solutions

        In this function you want to make a new solution, resolving conflict 
        and getting the lowest cost making two new solutions changing
        the solution of the drones you get and comparing both solutions
        """

        left_drone: Hub.Drone = conflict.get("drones")[0]
        rigth_drone: Hub.Drone = conflict.get("drones")[1]
        left_constraints: list[tuple] = self.constraints.copy()
        right_constraints: list[tuple] = self.constraints.copy()
        left_constraints.append(tuple([left_drone, conflict.get("v"),
                                       conflict.get("t")]))
        right_constraints.append(tuple([rigth_drone, conflict.get("v"),
                                        conflict.get("t")]))
        left_solutions = drone_map.update_solutions(left_constraints)
        right_solutions = drone_map.update_solutions(right_constraints)
        print(left_solutions)
        left_cost = self.calculate_cost(left_solutions)
        right_cost = self.calculate_cost(right_solutions)
        if left_cost < right_cost:
            self.re_define_values(left_constraints, left_solutions, left_cost)
        else:
            self.re_define_values(
                right_constraints, right_solutions, right_cost)

    def re_define_values(
            self, constraints: list[tuple],
            solutions: list, cost: int):
        """Function for adapting the main constraints tree"""
        self.constraints = constraints
        self.solutions = solutions
        self.cost = cost

    @staticmethod
    def calculate_cost(solutions) -> int:
        """function for calculating the cost of a solution"""
        cost: int = 0
        for _, path in solutions:
            for checkpoint in path:
                _, t, *_ = checkpoint
                if t > cost:
                    cost = t
        return cost

    def __str__(self) -> str:
        return f"constraints: {self.constraints}, solutions:" \
            f"{self.solutions}, cost: {self.cost} "
