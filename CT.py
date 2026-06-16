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
        constraints (list[tuple]): a list of constraints with the next
            structure (drone, hub/connection, time)
        solutions (list): a list of specific solution routes for each drone
        cost (int): the total cost of this solution
        left_node (CT): a new child generated because of the conflicts between
            drones
        rigth_node (CT): the other child
        swap (int): the integer specifying which branch to take in the decision
        last_conflict (Conflict | None): the last conflict checked
    """

    def __init__(
            self, constraints: list[Constraint], solutions: list[Solution]):
        self.constraints: list[Constraint] = constraints
        self.solutions: list[Solution] = solutions
        self.cost: int = self.calculate_cost(solutions)
        self.swap: int = 0
        self.last_conflict: Conflict | None = None

    @staticmethod
    def conflicts_equal(c1: Conflict, c2: Conflict) -> bool:
        """Check if two conflicts are equivalent.
        Compares two conflicts by vertex, timestep and drone set,
        regardless of drone order.

        Args:
            c1 (Conflict): First conflict to compare.
            c2 (Conflict): Second conflict to compare.

        Returns:
            bool: True if both conflicts share the same vertex, timestep
            and set of drones, False otherwise."""
        return (
            c1["v"] == c2["v"] and
            c1["t"] == c2["t"] and
            sorted(d.get_id() for
                   d in c1["drones"]) == sorted(d.get_id() for
                                                d in c2["drones"])
        )

    def create_new_tree(
            self, conflict: Conflict,
            drone_map: Map, solutions: list[Solution]) -> bool:
        """Generate a new constraint tree node to resolve a conflict.

        Creates two candidate branches by adding a constraint on each of
        the drones involved in the conflict, then selects the branch with
        the lowest total cost. If the conflict is identical to the previous
        one (loop detected), alternates between the optimal and suboptimal
        branch via self.swap to avoid getting stuck on the same conflict.

        Args:
            conflict (Conflict): Conflict to resolve, containing the vertex
                v, the timestep t and the two involved drones.
            drone_map (Map): Environment map, used to recalculate the
                restricted drone's solution via update_affected_solution.
            solutions (list[Solution]): Current solutions for all drones,
                used as the base for generating candidate branches.

        Returns:
            bool: Always True, indicating the node was created and the
            tree values updated successfully.

        Notes:
            self.swap acts as a tiebreaker on repeated conflicts: each
            repetition toggles it between 0 and 1, forcing exploration
            of the alternative branch when the optimal one does not converge.
        """

        if (self.last_conflict is not None):
            if self.conflicts_equal(self.last_conflict, conflict):
                if (self.swap == 0):
                    self.swap = 1
                else:
                    self.swap = 0
        self.last_conflict = conflict
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
        best_cost, best_constraints, best_solutions = branches[self.swap]

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
