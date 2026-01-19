import pandas as pd
import os
import re
import json

import pandas as pd


def build_problem_from_processed(
    processed_file,
    max_flood_risk=3
):
    df = pd.read_csv(processed_file)

    df["route_id"] = df["route_id"].astype(str)

    variables = df["route_id"].astype(str).tolist()

    # objective: waktu tempuh
    objective = dict(zip(
        df["route_id"],
        df["travel_time"]
    ))

    # flood constraint
    flood_score = dict(zip(
        df["route_id"],
        df["flood_score"]
    ))

    constraints = []

    # pilih minimal satu rute
    constraints.append(
        ({v: 1 for v in variables}, ">=", 1)
    )

    # batas risiko banjir
    constraints.append(
        ({v: flood_score[v] for v in variables}, "<=", max_flood_risk)
    )

    # binary upper bound
    for v in variables:
        constraints.append(({v: 1}, "<=", 1))

    return {
        "objective": objective,
        "constraints": constraints,
        "variables": variables
    }


# ======================================
# Mapping tingkat banjir → skor numerik
# ======================================
FLOOD_SCORE = {
    "Low": 0,
    "Moderate": 1,
    "High": 2,
    "Very_High": 5
}

# ======================================
# Utility
# ======================================
def normalize_route_id(x):
    """
    Konversi route_id menjadi format aman:
    int / bytes / str → r{number}
    contoh: 1 → r1
    """
    if isinstance(x, bytes):
        x = x.decode("utf-8", errors="ignore")

    x = str(x).strip()

    # jika murni angka → tambahkan prefix r
    if re.fullmatch(r"\d+", x):
        x = f"r{x}"

    # sanitasi karakter ilegal (jaga-jaga)
    x = re.sub(r"[^a-zA-Z0-9_]", "_", x)

    return x



# ======================================
# Load data mentah
# ======================================
def load_raw_data(flood_file, time_file):
    flood_df = pd.read_excel(flood_file, engine="openpyxl")
    time_df = pd.read_excel(time_file, engine="xlrd")
    return flood_df, time_df


# ======================================
# Preprocessing utama
# ======================================
def preprocess_and_save(
    flood_file,
    time_file,
    output_dir="../data/processed"
):
    flood_df, time_df = load_raw_data(flood_file, time_file)

    # ----------------------------
    # Normalisasi route_id
    # ----------------------------
    flood_df["route_id"] = flood_df["route_id"].apply(normalize_route_id)
    time_df["route_id"] = time_df["route_id"].apply(normalize_route_id)

    # ----------------------------
    # Mapping banjir → skor
    # ----------------------------
    flood_df["flood_score"] = flood_df["SUSCEP"].map(FLOOD_SCORE)

    if flood_df["flood_score"].isna().any():
        bad = flood_df[flood_df["flood_score"].isna()]
        raise ValueError(
            f"Kategori banjir tidak dikenal:\n{bad[['route_id','SUSCEP']]}"
        )

    # ----------------------------
    # Ambil kolom penting saja
    # ----------------------------
    flood_df = flood_df[["route_id", "flood_score"]]
    time_df = time_df[["route_id", "Duration"]]

    # ----------------------------
    # Join → hanya rute valid
    # ----------------------------
    routes_df = pd.merge(
        time_df,
        flood_df,
        on="route_id",
        how="inner"
    )

    if routes_df.empty:
        raise ValueError("Tidak ada route yang cocok antara dua dataset")

    # ----------------------------
    # Rename kolom agar jelas
    # ----------------------------
    routes_df = routes_df.rename(columns={
        "Duration": "travel_time"
    })

    # ----------------------------
    # Sort agar konsisten
    # ----------------------------
    routes_df = routes_df.sort_values("route_id").reset_index(drop=True)

    # ----------------------------
    # Simpan hasil
    # ----------------------------
    os.makedirs(output_dir, exist_ok=True)

    csv_path = os.path.join(output_dir, "routes_processed.csv")
    xlsx_path = os.path.join(output_dir, "routes_processed.xlsx")

    routes_df.to_csv(csv_path, index=False)
    routes_df.to_excel(xlsx_path, index=False)

    print("✅ Preprocessing selesai")
    print(f"📄 CSV  : {csv_path}")
    print(f"📄 XLSX : {xlsx_path}")

    return routes_df


def export_problem_to_json(problem, output_path):
    """
    Export problem dictionary ke JSON (aman untuk numpy / set).
    """
    def convert(obj):
        if isinstance(obj, set):
            return list(obj)
        if hasattr(obj, "tolist"):   # numpy array
            return obj.tolist()
        if hasattr(obj, "__dict__"):
            return obj.__dict__
        return obj

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(problem, f, indent=4, default=convert)

    print(f"[OK] Problem exported to JSON: {output_path}")
