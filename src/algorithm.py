import math
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
        """
        Solve LP relaxation untuk maximization.
        Constraints format: (coeff_dict, sense, rhs)
        sense: "<=" or ">="
        """
        variables = self.problem["variables"]
        obj_coeff = self.problem["objective"]
        
        # Gabungkan semua constraints
        all_constraints = []
        
        # 1. Base constraints dari problem
        for lhs, sense, rhs in self.problem["constraints"]:
            all_constraints.append((lhs, sense, rhs))
            
        # 2. Constraints dari branching
        for (var, sense, value) in node.constraints:
            all_constraints.append(({var: 1.0}, sense, value))
            
        # 3. Non-negativity constraints (implisit x ≥ 0)
        # Ini akan ditangani oleh lower bound default 0
        
        # Konversi ke bentuk standar (<=)
        standard_constraints = []
        for lhs, sense, rhs in all_constraints:
            if sense == "<=":
                standard_constraints.append((lhs, rhs))
            elif sense == ">=":
                # Kalikan dengan -1 untuk konversi ke <=
                new_lhs = {k: -v for k, v in lhs.items()}
                standard_constraints.append((new_lhs, -rhs))
                
        n_vars = len(variables)
        n_constraints = len(standard_constraints)
        
        # Buat indeks untuk variabel
        var_index = {var: i for i, var in enumerate(variables)}
        
        # Inisialisasi tableau: (n_constraints + 1) x (n_vars + n_constraints + 1)
        tableau = [[0.0] * (n_vars + n_constraints + 1) for _ in range(n_constraints + 1)]
        
        # 1. Isi constraint rows
        for i in range(n_constraints):
            lhs, rhs = standard_constraints[i]
            # Koefisien variabel asli
            for var, coeff in lhs.items():
                j = var_index[var]
                tableau[i][j] = coeff
            # Slack variable (1 di kolomnya)
            tableau[i][n_vars + i] = 1.0
            # RHS
            tableau[i][-1] = rhs
            
        # 2. Isi objective row (MAXIMIZATION: kita akan maximize c^T x)
        # Di tableau simplex standar, row terakhir adalah -c untuk maximization
        for j, var in enumerate(variables):
            tableau[-1][j] = -obj_coeff.get(var, 0.0)  # Negatif karena kita maximize
        
        # 3. Pastikan RHS non-negatif (untuk fase I sederhana)
        for i in range(n_constraints):
            if tableau[i][-1] < -1e-9:
                # Kalau RHS negatif, kalikan seluruh row dengan -1
                for j in range(len(tableau[i])):
                    tableau[i][j] = -tableau[i][j]
        
        # 4. Simpleks iterasi (dengan Bland's rule)
        EPS = 1e-9
        MAX_ITER = 1000
        iter_count = 0
        
        def pivot(pivot_row, pivot_col):
            pivot_val = tableau[pivot_row][pivot_col]
            # Normalize pivot row
            for j in range(len(tableau[pivot_row])):
                tableau[pivot_row][j] /= pivot_val
                
            # Eliminate pivot column dari rows lain
            for i in range(len(tableau)):
                if i != pivot_row:
                    factor = tableau[i][pivot_col]
                    for j in range(len(tableau[i])):
                        tableau[i][j] -= factor * tableau[pivot_row][j]
        
        while True:
            iter_count += 1
            if iter_count > MAX_ITER:
                node.lp_status = "infeasible"
                return
                
            # Cari entering variable (most negative di objective row)
            entering_col = None
            min_val = 0
            for j in range(n_vars + n_constraints):
                if tableau[-1][j] < min_val - EPS:
                    min_val = tableau[-1][j]
                    entering_col = j
                    
            if entering_col is None:
                break  # Optimal
                
            # Minimum ratio test
            min_ratio = float('inf')
            pivot_row = None
            for i in range(n_constraints):
                if tableau[i][entering_col] > EPS:
                    ratio = tableau[i][-1] / tableau[i][entering_col]
                    if ratio < min_ratio - EPS:
                        min_ratio = ratio
                        pivot_row = i
                        
            if pivot_row is None:
                node.lp_status = "unbounded"
                return
                
            pivot(pivot_row, entering_col)
            
        # 5. Ekstrak solusi
        solution = {var: 0.0 for var in variables}
        objective_value = 0.0
        
        # Untuk setiap variable asli
        for j, var in enumerate(variables):
            # Cek jika ini basic variable
            col = [tableau[i][j] for i in range(n_constraints)]
            # Basic variable punya tepat satu 1 dan lainnya 0
            if sum(abs(val) for val in col) > 1 + EPS:
                continue
                
            one_count = sum(1 for val in col if abs(val - 1.0) < EPS)
            zero_count = sum(1 for val in col if abs(val) < EPS)
            
            if one_count == 1 and zero_count == n_constraints - 1:
                pivot_row = next(i for i in range(n_constraints) if abs(tableau[i][j] - 1.0) < EPS)
                solution[var] = tableau[pivot_row][-1]
                
            objective_value += obj_coeff.get(var, 0.0) * solution[var]
            
        node.lp_solution = solution
        node.lp_objective = objective_value
        node.lp_status = "optimal"
        
        # Debug output
        print(f"Node {node.id}: LP solution = {solution}, objective = {objective_value}")

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

