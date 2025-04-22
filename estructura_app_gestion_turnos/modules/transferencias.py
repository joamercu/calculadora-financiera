# Archivo: transferencias.py
import streamlit as st
from datetime import datetime
from modules.turnos import GRUPOS

def formulario_transferencia(tareas_df):
    if tareas_df.empty:
        st.warning("⚠️ No hay tareas disponibles para transferencia.")
        return

    st.header("🔁 Transferencia de Turno")

    hoy = datetime.now()
    with st.form("form_transferencia"):
        fecha = st.date_input("📅 Fecha de entrega", value=hoy.date())
        entrega = st.selectbox("Grupo que entrega", GRUPOS)
        recibe = st.selectbox("Grupo que recibe", GRUPOS)
        tarea = st.selectbox("Tarea a transferir", tareas_df["ID"])
        observaciones = st.text_area("📌 Observaciones")
        enviado = st.form_submit_button("Registrar transferencia")

    if enviado:
        st.success(f"✅ Transferencia registrada: {entrega} ➡️ {recibe} | Tarea: {tarea}")
