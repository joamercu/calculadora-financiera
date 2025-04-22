# Archivo: excel_export.py
import streamlit as st
import pandas as pd
from io import BytesIO  # ← ESTA LÍNEA ES CLAVE
from datetime import datetime

def exportar_excel(df, nombre_archivo: str = None):
    if df.empty:
        st.warning("⚠️ No hay datos para exportar.")
        return

    if not nombre_archivo:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"reporte_a_gerencia_{timestamp}.xlsx"

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Datos")

    output.seek(0)

    st.download_button(
        label="⬇️ Descargar Excel",
        data=output,
        file_name=nombre_archivo,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
