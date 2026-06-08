from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Map import Map

from typing import TypedDict
from Hub import Connection, Hub


class Conflict(TypedDict):
    v: str | Connection
    t: int
    drones: list[Hub.Drone]


Checkpoint = tuple[str, int, Connection]
Solution = tuple[Hub.Drone, list[Checkpoint]]
Constraint = tuple[Hub.Drone, str | Connection, int]


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

    def __init__(
            self, constraints: list[Constraint], solutions: list[Solution]):
        print(solutions)
        self.constraints: list[Constraint] = constraints
        self.solutions: list[Solution] = solutions
        self.cost: int = self.calculate_cost(solutions)

    def create_new_tree(
            self, conflict: Conflict,
            drone_map: Map, solutions: list[Solution]) -> bool:

        left_drone: Hub.Drone = conflict.get("drones")[0]
        right_drone: Hub.Drone = conflict.get("drones")[1]

        left_constraints = self.constraints.copy()
        left_constraints.append(
            (left_drone, conflict.get("v"), conflict.get("t")))
        left_solutions = drone_map.update_affected_solution(
            left_drone, left_constraints, solutions)
        left_cost = self.calculate_cost(left_solutions)

        right_constraints = self.constraints.copy()
        right_constraints.append(
            (right_drone, conflict.get("v"), conflict.get("t")))
        right_solutions = drone_map.update_affected_solution(
            right_drone, right_constraints, solutions)
        right_cost = self.calculate_cost(right_solutions)

        branches = sorted(
            [(left_cost,  left_constraints,  left_solutions),
             (right_cost, right_constraints, right_solutions)],
            key=lambda x: x[0]
        )
        best_cost, best_constraints, best_solutions = branches[1]

        self.re_define_values(best_constraints, best_solutions, best_cost)
        return True

    def re_define_values(
            self, constraints: list[Constraint],
            solutions: list[Solution], cost: int) -> None:
        """Function for adapting the main constraints tree"""
        self.constraints = constraints
        self.solutions = solutions
        self.cost = cost

    @staticmethod
    def calculate_cost(solutions: list[Solution]) -> int:
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
