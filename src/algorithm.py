import math
from utils import is_integer

class BBNode:
    def __init__(self):
        # --- Basic node info ---
        self.id: int = None
        self.depth: int = None
        self.parent: "BBNode" = None

        # --- Problem definition ---
        self.constraints: list = []
        self.variable_bounds: dict = {}

        # --- LP relaxation solution ---
        self.lp_solution: dict = {} # e.g. {'x1': 1.67, 'x2': 0}
        self.lp_objective: float = None
        self.lp_status: str = None  # e.g. 'optimal', 'infeasible'

        # --- Branching information ---
        self.branching_variable: int = None
        self.branching_direction: str = None  # "≤" or "≥"
        self.branching_value: float = None

        # --- Node status ---
        self.is_fathomed: bool = False
        self.fathom_reason: str = None

        # --- Children ---
        self.left_child: "BBNode" = None
        self.right_child: "BBNode" = None


"""
Main Branch and Bound solver class.
"""
class BranchAndBound:
    """
    Initialize the Branch and Bound algorithm.

    Parameters:
    - problem: an integer programming problem definition
    """
    def __init__(self, problem):
        self.problem = problem

        self.root = None
        self.active_nodes = []
        self.incumbent_solution = None
        self.incumbent_value = None

        self.node_counter = 0

    """
    Main Branch and Bound loop (high-level algorithm).
    """
    def solve(self):
        # Step 1: Initialization
        self.root = BBNode()
        self.root.id = self.node_counter
        self.root.depth = 0
        self.root.parent = None

        self.active_nodes.append(self.root)

        self.incumbent_solution = None
        self.incumbent_value = float("-inf")  # For maximization

        # Step 2: Main Loop
        while self.active_nodes:

            # --- Node selection ---
            current_node = self.select_node()
            self.active_nodes.remove(current_node)
            self.node_counter += 1

            # --- Solve LP relaxation ---
            self.solve_lp(current_node)

            # --- Fathoming checks ---
            self.check_fathom(current_node)
            if current_node.is_fathomed:
                continue

            # --- Branching ---
            self.branch(current_node)

        # =========================
        # Step 3: Return result
        # =========================
        if self.incumbent_solution is None:
            return "Infeasible"
        else:
            return (
                self.incumbent_solution,
                self.incumbent_value,
                self.node_counter,
            )

    """
    Select the next node to explore.
    Could implement DFS, BFS, or Best-First.
    """
    def select_node(self):
        # TODO: Select node from self.active_nodes
        pass


    def solve_lp(self, node):
        """
        Solve LP relaxation using a simplified (educational) simplex method.
        Assumptions:
        - Maximization
        - All constraints are <= after transformation
        - x >= 0
        """

        # =========================
        # 1. Build LP model
        # =========================
        variables = self.problem["variables"]
        obj = self.problem["objective"]
        base_constraints = self.problem["constraints"]

        # Gabungkan constraint global + node constraint
        constraints = base_constraints.copy()

        for (var, sense, value) in node.constraints:
            if sense == "<=":
                constraints.append(({var: 1}, "<=", value))
            elif sense == ">=":
                # ubah x >= k menjadi -x <= -k
                constraints.append(({var: -1}, "<=", -value))

        n = len(variables)
        m = len(constraints)

        # =========================
        # 2. Build simplex tableau
        # =========================
        # Tableau size: (m + 1) x (n + m + 1)
        tableau = [[0.0 for _ in range(n + m + 1)] for _ in range(m + 1)]

        # Constraint rows
        for i, (lhs, _, rhs) in enumerate(constraints):
            for j, var in enumerate(variables):
                tableau[i][j] = lhs.get(var, 0.0)

            tableau[i][n + i] = 1.0      # slack variable
            tableau[i][-1] = rhs         # RHS

        # Objective row (negated for maximization)
        for j, var in enumerate(variables):
            tableau[-1][j] = -obj.get(var, 0.0)

        # =========================
        # 3. Simplex iterations
        # =========================
        def pivot(pivot_row, pivot_col):
            pivot_value = tableau[pivot_row][pivot_col]
            tableau[pivot_row] = [x / pivot_value for x in tableau[pivot_row]]

            for i in range(len(tableau)):
                if i != pivot_row:
                    factor = tableau[i][pivot_col]
                    tableau[i] = [
                        tableau[i][j] - factor * tableau[pivot_row][j]
                        for j in range(len(tableau[i]))
                    ]

        while True:
            # Cari entering variable (paling negatif di objective row)
            last_row = tableau[-1][:-1]
            min_value = min(last_row)

            if min_value >= -1e-9:
                break  # optimal

            pivot_col = last_row.index(min_value)

            # Cari leaving variable (minimum ratio test)
            ratios = []
            for i in range(m):
                col_value = tableau[i][pivot_col]
                if col_value > 1e-9:
                    ratios.append((tableau[i][-1] / col_value, i))

            if not ratios:
                node.lp_status = "infeasible"
                return

            _, pivot_row = min(ratios)
            pivot(pivot_row, pivot_col)

        # =========================
        # 4. Extract solution
        # =========================
        solution = {var: 0.0 for var in variables}

        for j, var in enumerate(variables):
            col = [tableau[i][j] for i in range(m)]
            if col.count(1.0) == 1 and col.count(0.0) == m - 1:
                row = col.index(1.0)
                solution[var] = tableau[row][-1]

        node.lp_solution = solution
        node.lp_objective = tableau[-1][-1]
        node.lp_status = "optimal"

    """
    Check fathoming conditions:
    - infeasible
    - integer solution
    - bound worse than incumbent
    Parameters:
    - node: BBNode
    """
    def check_fathom(self, node):
        # 1. Infeasible LP
        if node.lp_status == "infeasible":
            node.is_fathomed = True
            node.fathom_reason = "Infeasible LP"
            return

        # 2. Bound worse than incumbent
        if node.lp_objective <= self.incumbent_value:
            node.is_fathomed = True
            node.fathom_reason = "Bound worse than incumbent"
            return

        # 3. Integer solution
        if is_integer(node.lp_solution):
            if node.lp_objective > self.incumbent_value:
                self.incumbent_solution = node.lp_solution
                self.incumbent_value = node.lp_objective

            node.is_fathomed = True
            node.fathom_reason = "Integer solution"
            return

    """
    Perform branching on a fractional variable.
    Parameters:
    - node: BBNode
    """
    def branch(self, node):
        """
        Perform branching on a fractional variable.
        Create two child nodes:
        - Left child: x_j <= floor(value)
        - Right child: x_j >= ceil(value)
        """

        # 1. Select branching variable (sesuai pseudocode dosen)
        var = self._select_branch_variable(node.lp_solution)

        if var is None:
            return  # seharusnya tidak terjadi jika fathoming benar

        value = node.lp_solution[var]
        floor_val = math.floor(value)
        ceil_val = math.ceil(value)

        # 2. LEFT CHILD: x_j <= floor(value)
        left = BBNode()
        left.id = self.node_counter
        self.node_counter += 1

        left.depth = node.depth + 1
        left.parent = node

        left.constraints = node.constraints.copy()
        left.constraints.append((var, "<=", floor_val))

        left.variable_bounds = node.variable_bounds.copy()

        # Info branching
        left.branching_variable = var
        left.branching_direction = "<="
        left.branching_value = floor_val

        # 3. RIGHT CHILD: x_j >= ceil(value)
        right = BBNode()
        right.id = self.node_counter
        self.node_counter += 1

        right.depth = node.depth + 1
        right.parent = node

        right.constraints = node.constraints.copy()
        right.constraints.append((var, ">=", ceil_val))

        right.variable_bounds = node.variable_bounds.copy()

        # Info branching
        right.branching_variable = var
        right.branching_direction = ">="
        right.branching_value = ceil_val

        # 4. Hubungkan ke parent (tree structure)
        node.left_child = left
        node.right_child = right

        # 5. Tambahkan ke daftar node aktif
        self.active_nodes.append(left)
        self.active_nodes.append(right)


    """
    Visualize the Branch and Bound tree.
    Actual plotting should be implemented in visualization.py
    """
    def visualize_tree(self):
        # TODO: Call visualization utilities
        pass

    def _fractionality(self, x):
        floor_dist = x - math.floor(x)
        ceil_dist = math.ceil(x) - x
        return min(floor_dist, ceil_dist)
    
    def _select_branch_variable(self, lp_solution):
        """
        Select branching variable using 'most fractional' rule.
        INPUT: lp_solution (dict)
        OUTPUT: variable name (key) or None
        """

        fractional_vars = []

        # Find fractional variables
        for var, value in lp_solution.items():
            if abs(value - round(value)) > 1e-5:
                fractional_vars.append(var)

        # All integer
        if not fractional_vars:
            return None

        # Apply selection rule (most fractional)
        best_var = fractional_vars[0]
        best_frac = self._fractionality(lp_solution[best_var])

        for var in fractional_vars:
            frac = self._fractionality(lp_solution[var])
            if frac > best_frac:
                best_var = var
                best_frac = frac

        return best_var
    

# Input Asumptions:
# problem = {
#     "objective": {"x1": 3, "x2": 2},   # max 3x1 + 2x2
#     "constraints": [
#         ({"x1": 2, "x2": 1}, "<=", 18),
#         ({"x1": 2, "x2": 3}, "<=", 42),
#         ({"x1": 3, "x2": 1}, "<=", 24),
#     ],
#     "variables": ["x1", "x2"]
# }
