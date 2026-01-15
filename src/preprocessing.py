def build_problem(items, total_time_available):
    """
    Mengubah input dinamis user menjadi format problem
    yang siap digunakan oleh algoritma Branch and Bound
    """

    objective = {}
    constraints = []
    variables = []

    # mapping nama barang -> variabel internal (x1, x2, ...)
    var_map = {}

    # =========================
    # Generate variables & objective
    # =========================
    for idx, item in enumerate(items, start=1):
        var_name = f"x{idx}"
        var_map[item["name"]] = var_name
        variables.append(var_name)

        # objective: keuntungan
        objective[var_name] = item["profit"]

        # constraint: bahan baku per barang
        constraints.append(
            ({var_name: item["material_per_unit"]}, "<=", item["material_available"])
        )

    # =========================
    # Constraint: waktu bersama
    # =========================
    time_constraint_lhs = {}

    for idx, item in enumerate(items, start=1):
        var_name = f"x{idx}"
        time_constraint_lhs[var_name] = item["time_per_unit"]

    constraints.append((time_constraint_lhs, "<=", total_time_available))

    # =========================
    # Final problem
    # =========================
    problem = {
        "objective": objective,
        "constraints": constraints,
        "variables": variables,
    }

    return problem, var_map
