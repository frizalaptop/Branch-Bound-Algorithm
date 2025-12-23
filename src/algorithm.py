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
        self.lp_solution: dict = {}
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
        Main Branch and Bound loop.
        """
        # TODO: Initialize root node
        # TODO: While active nodes exist:
        #       - select node
        #       - solve LP relaxation
        #       - check fathoming conditions
        #       - branch if necessary
        #       - update incumbent
        pass

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
