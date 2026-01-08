import math
import pulp
from utils import is_integer

class BBNode:
    def __init__(self):
        # --- Basic node info ---
        self.id: int = None
        self.depth: int = None
        self.parent: "BBNode" = None

        # --- Problem definition ---
        self.constraints: list = []  # List of (var, sense, value)
        self.variable_bounds: dict = {}

        # --- LP relaxation solution ---
        self.lp_solution: dict = {} 
        self.lp_objective: float = None
        self.lp_status: str = None  # 'optimal', 'infeasible'

        # --- Branching information ---
        self.branching_variable: str = None
        self.branching_direction: str = None  # "≤" or "≥"
        self.branching_value: float = None

        # --- Node status ---
        self.is_fathomed: bool = False
        self.fathom_reason: str = None

        # --- Children ---
        self.left_child: "BBNode" = None
        self.right_child: "BBNode" = None


class BranchAndBound:
    def __init__(self, problem):
        self.problem = problem
        self.root = None
        self.active_nodes = []
        self.incumbent_solution = None
        self.incumbent_value = None
        self.node_counter = 0

        # --- Visited Nodes ---
        self.visited_nodes = set()

    def solve(self):
        # Step 1: Initialization
        self.root = BBNode()
        self.root.id = self.node_counter
        self.root.depth = 0
        self.root.parent = None
        self.active_nodes.append(self.root)
        
        # Untuk maximization, incumbent_value mulai dari -∞
        self.incumbent_solution = None
        self.incumbent_value = float("-inf")

        # Step 2: Main Loop
        while self.active_nodes:
            # --- Node selection (DFS) ---
            current_node = self.active_nodes[-1]  # LIFO untuk DFS
            self.active_nodes.pop()

            signature = self._node_signature(current_node)
            if signature in self.visited_nodes:
                continue

            self.visited_nodes.add(signature)

            
            # --- Solve LP relaxation ---
            self.solve_lp(current_node)
            
            # --- Fathoming checks ---
            self.check_fathom(current_node)
            if current_node.is_fathomed:
                continue
                
            # --- Branching ---
            self.branch(current_node)

        # Step 3: Return result
        if self.incumbent_solution is None:
            return "Infeasible"
        else:
            return (
                self.incumbent_solution,
                self.incumbent_value,
                self.node_counter,
            )

    def solve_lp(self, node):
            variables = self.problem["variables"]
            obj_coeff = self.problem["objective"]

            # 1. Definisikan problem LP (MAX)
            prob = pulp.LpProblem("LP_relaxation", pulp.LpMaximize)

            # 2. Definisikan variabel (continuous, >= 0)
            lp_vars = {
                v: pulp.LpVariable(v, lowBound=0, cat="Continuous")
                for v in variables
            }

            # 3. Objective
            prob += pulp.lpSum(obj_coeff[v] * lp_vars[v] for v in variables)

            # 4. Base constraints
            for lhs, sense, rhs in self.problem["constraints"]:
                expr = pulp.lpSum(lhs[v] * lp_vars[v] for v in lhs)
                if sense == "<=":
                    prob += expr <= rhs
                elif sense == ">=":
                    prob += expr >= rhs

            # 5. Branching constraints
            for var, sense, value in node.constraints:
                if sense == "<=":
                    prob += lp_vars[var] <= value
                elif sense == ">=":
                    prob += lp_vars[var] >= value

            # 6. Solve
            status = prob.solve(pulp.PULP_CBC_CMD(msg=False))

            if status != pulp.LpStatusOptimal:
                node.lp_status = "infeasible"
                return

            # 7. Extract solution
            node.lp_solution = {v: lp_vars[v].value() for v in variables}
            node.lp_objective = pulp.value(prob.objective)
            node.lp_status = "optimal"

            print(f"Node {node.id}: LP solution = {node.lp_solution}, objective = {node.lp_objective}")

    def check_fathom(self, node):
        # 1. Infeasible LP
        if node.lp_status != "optimal":
            node.is_fathomed = True
            node.fathom_reason = "Infeasible or unbounded LP"
            return
            
        # 2. Bound worse than incumbent (untuk maximization)
        if node.lp_objective <= self.incumbent_value + 1e-9:
            node.is_fathomed = True
            node.fathom_reason = "Bound worse than incumbent"
            return
            
        # 3. Integer solution check
        all_integer = True
        for value in node.lp_solution.values():
            if not is_integer(value):
                all_integer = False
                break
                
        if all_integer:
            # Update incumbent jika lebih baik
            if node.lp_objective > self.incumbent_value:
                self.incumbent_solution = {
                    k: round(v) for k, v in node.lp_solution.items()
                }
                self.incumbent_value = node.lp_objective
                print(f"New incumbent: {self.incumbent_solution}, value: {self.incumbent_value}")
                
            node.is_fathomed = True
            node.fathom_reason = "Integer solution"
            return

    def branch(self, node):
        # Cari variable fractional untuk di-branch
        branch_var = None
        max_fractionality = -1
        
        for var, value in node.lp_solution.items():
            frac = min(value - math.floor(value), math.ceil(value) - value)
            if frac > 1e-9 and frac > max_fractionality:
                max_fractionality = frac
                branch_var = var
                
        if branch_var is None:
            return
            
        value = node.lp_solution[branch_var]
        floor_val = math.floor(value)
        ceil_val = math.ceil(value)
        
        # Left child: x <= floor(value)
        left_child = BBNode()
        left_child.id = self.node_counter
        self.node_counter += 1
        left_child.depth = node.depth + 1
        left_child.parent = node
        left_child.constraints = node.constraints.copy()
        left_child.constraints.append((branch_var, "<=", floor_val))
        
        # Right child: x >= ceil(value)
        right_child = BBNode()
        right_child.id = self.node_counter
        self.node_counter += 1
        right_child.depth = node.depth + 1
        right_child.parent = node
        right_child.constraints = node.constraints.copy()
        right_child.constraints.append((branch_var, ">=", ceil_val))
        
        # Tambahkan ke active nodes (DFS: tambahkan right dulu, lalu left)
        self.active_nodes.append(right_child)
        self.active_nodes.append(left_child)
        
        print(f"Branching on {branch_var} = {value:.3f}")
        print(f"  Left: {branch_var} <= {floor_val}")
        print(f"  Right: {branch_var} >= {ceil_val}")
    
    
    def _node_signature(self, node):
        # sort supaya canonical
        return tuple(sorted(node.constraints))

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

