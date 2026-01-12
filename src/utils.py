def is_integer(value, tol=1e-9):
    return abs(value - round(value)) < tol
