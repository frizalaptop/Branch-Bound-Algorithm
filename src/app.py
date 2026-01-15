# app.py

import streamlit as st
from preprocessing import build_problem
from algorithm import BranchAndBound


st.set_page_config(page_title="Branch & Bound - Problem Builder", layout="wide")

st.title("📦 Integer Programming Problem Builder")
st.markdown(
    """
    UI ini digunakan untuk **membangun problem Integer Programming secara dinamis**
    sebelum diproses oleh algoritma **Branch and Bound**.
    """
)

# =========================
# Input jumlah barang
# =========================
num_items = st.number_input(
    "Jumlah Barang",
    min_value=1,
    step=1,
    value=3,
)

st.divider()

# =========================
# Input data tiap barang
# =========================
items = []

st.subheader("🧾 Data Barang")

for i in range(num_items):
    with st.expander(f"Barang {i + 1}", expanded=True):
        name = st.text_input(f"Nama Barang", key=f"name_{i}")
        profit = st.number_input(
            f"Keuntungan per unit",
            min_value=0,
            step=1,
            key=f"profit_{i}",
        )
        material_per_unit = st.number_input(
            f"Bahan baku per unit",
            min_value=0,
            step=1,
            key=f"material_unit_{i}",
        )
        material_available = st.number_input(
            f"Bahan baku tersedia",
            min_value=0,
            step=1,
            key=f"material_avail_{i}",
        )
        time_per_unit = st.number_input(
            f"Waktu produksi per unit",
            min_value=0,
            step=1,
            key=f"time_{i}",
        )

        if name:
            items.append(
                {
                    "name": name,
                    "profit": profit,
                    "material_per_unit": material_per_unit,
                    "material_available": material_available,
                    "time_per_unit": time_per_unit,
                }
            )

st.divider()

# =========================
# Input waktu total
# =========================
st.subheader("⏱️ Kendala Waktu")

total_time_available = st.number_input(
    "Total waktu tersedia",
    min_value=0,
    step=1,
    value=56,
)

# =========================
# Generate problem
# =========================
st.divider()

if st.button("🚀 Generate & Solve Problem"):
    if len(items) != num_items:
        st.error("⚠️ Semua barang harus memiliki nama.")
    else:
        problem, var_map = build_problem(items, total_time_available)

        st.success("Problem berhasil dibuat!")

        st.subheader("📌 Problem Dictionary")
        st.code(problem, language="python")

        # =========================
        # Jalankan Branch & Bound
        # =========================
        solver = BranchAndBound(problem)
        solution, value, nodes = solver.solve()

        st.subheader("✅ Hasil Optimasi (Integer Solution)")
        st.write(f"**Nilai objektif maksimum:** {value}")
        st.write(f"**Jumlah node dieksplorasi:** {nodes}")

        st.subheader("📦 Solusi dalam Variabel Internal")
        st.code(solution, language="python")

        # =========================
        # Konversi ke nama barang
        # =========================
        readable_solution = {}
        for item_name, var in var_map.items():
            readable_solution[item_name] = solution.get(var, 0)

        st.subheader("🧾 Solusi dalam Nama Barang")
        st.code(readable_solution, language="python")
