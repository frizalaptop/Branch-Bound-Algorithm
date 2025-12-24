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



class BranchAndBound:
    """
    Main Branch and Bound solver class.
    """

    def __init__(self, problem):
        """
        Initialize the Branch and Bound algorithm.

        Parameters:
        - problem: an integer programming problem definition
        """
        self.problem = problem

        self.root = None
        self.active_nodes = []
        self.incumbent_solution = None
        self.incumbent_value = None

        self.node_counter = 0

    def solve(self):
        """
        Main Branch and Bound loop (high-level algorithm).
        """
        # =========================
        # Step 1: Initialization
        # =========================
        self.root = BBNode()
        self.root.id = self.node_counter
        self.root.depth = 0
        self.root.parent = None

        self.active_nodes.append(self.root)

        self.incumbent_solution = None
        self.incumbent_value = float("-inf")  # For maximization

        # =========================
        # Step 2: Main Loop
        # =========================
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

            # --- Check for integer solution ---
            # (Handled conceptually inside check_fathom or here)
            if current_node.lp_solution is not None:
                # Placeholder for integer-solution check
                is_integer_solution = False  # TODO

                if is_integer_solution:
                    if current_node.lp_objective > self.incumbent_value:
                        self.incumbent_solution = current_node.lp_solution
                        self.incumbent_value = current_node.lp_objective

                    current_node.is_fathomed = True
                    current_node.fathom_reason = "Integer solution"
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

    def select_node(self):
        """
        Select the next node to explore.
        Could implement DFS, BFS, or Best-First.
        """
        # TODO: Select node from self.active_nodes
        pass

    def solve_lp(self, node):
        """
        Solve the LP relaxation for a given node.

        Parameters:
        - node: BBNode
        """
        # TODO: Solve LP relaxation using node constraints
        pass

    def check_fathom(self, node):
        """
        Check fathoming conditions:
        - infeasible
        - integer solution
        - bound worse than incumbent

        Parameters:
        - node: BBNode
        """
        # TODO: Determine whether the node should be fathomed
        pass

    def branch(self, node):
        """
        Perform branching on a fractional variable.

        Parameters:
        - node: BBNode
        """
        # TODO: Select branching variable
        # TODO: Create child nodes with additional constraints
        pass

    def visualize_tree(self):
        """
        Visualize the Branch and Bound tree.
        Actual plotting should be implemented in visualization.py
        """
        # TODO: Call visualization utilities
        pass
