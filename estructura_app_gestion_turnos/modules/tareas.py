# Archivo: tareas.py
import streamlit as st
import pandas as pd
import os

GRUPOS = ["Grupo A", "Grupo B", "Grupo C", "Grupo D"]


def mostrar_tareas():
    st.header("📝 Tareas en Curso")

    tareas_path = "data/tareas.xlsx"
    if os.path.exists(tareas_path):
        try:
            tareas_df = pd.read_excel(tareas_path)
        except Exception as e:
            st.error(f"❌ Error al leer el archivo de tareas: {e}")
            return pd.DataFrame()
    else:
        st.warning("⚠️ No se encontró el archivo de tareas. Se mostrará una tabla de ejemplo.")
        tareas_df = pd.DataFrame({
            "ID": ["T001", "T002"],
            "Grupo": ["Grupo A", "Grupo B"],
            "Descripción": ["Inspección de válvulas", "Soldadura criogénica"],
            "Estado": ["En curso", "Pausada"]
        })

    filtro_grupo = st.selectbox("🔍 Filtrar por grupo", ["Todos"] + GRUPOS)
    if filtro_grupo != "Todos":
        tareas_df = tareas_df[tareas_df["Grupo"] == filtro_grupo]

    st.dataframe(tareas_df, use_container_width=True)

    return tareas_df
