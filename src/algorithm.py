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

    """
    Solve the LP relaxation for a given node.
    Parameters:
    - node: BBNode
    """
    def solve_lp(self, node):
        
        # TODO: Solve LP relaxation using node constraints
        pass

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
        if self.is_integer_solution(node.lp_solution):
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
        # TODO: Select branching variable
        # TODO: Create child nodes with additional constraints
        pass


    """
    Visualize the Branch and Bound tree.
    Actual plotting should be implemented in visualization.py
    """
    def visualize_tree(self):
        # TODO: Call visualization utilities
        pass
