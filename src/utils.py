def is_integer(lp_solution, tol=1e-5):
    """
    Check whether all values in an LP solution dictionary
    are integer within numerical tolerance.

    Parameters:
    - lp_solution: dict, e.g. {'x1': 1.67, 'x2': 0}
    - tol: numerical tolerance

    Returns:
    - bool
    """
    if lp_solution is None:
        return False

    for value in lp_solution.values():
        if not isinstance(value, (int, float)):
            return False
        if abs(value - round(value)) > tol:
            return False

    return True
