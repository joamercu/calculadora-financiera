# Archivo principal: app_streamlit.py
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import pytz

from modules.reloj import mostrar_reloj
from modules.tareas import mostrar_tareas
from modules.transferencias import formulario_transferencia
from modules.upload import cargar_excel_estado
from modules.excel_export import exportar_excel

# ==================== CONFIGURACIONES ==================== #
st.set_page_config(page_title="Gestión de Turnos 14x7", layout="wide")
st.title("🕒 Gestión de Turnos, Tareas y Transferencias PROYECTOS METALMECANICA")

# ==================== SELECCIÓN DE MÓDULOS ==================== #
modulo = st.sidebar.selectbox("📂 Selecciona un módulo", [
    "Reloj y Turno Actual",
    "Tareas en Curso",
    "Transferencia de Turno",
    "Carga de Estado de Tareas",
    "Exportar a Excel",
    "Calendario de Turnos"  # ⬅️ NUEVO
])

# ==================== LLAMADO A MÓDULOS ==================== #
if modulo == "Reloj y Turno Actual":
    mostrar_reloj()

elif modulo == "Tareas en Curso":
    tareas_df = mostrar_tareas()

elif modulo == "Transferencia de Turno":
    tareas_df = mostrar_tareas()
    formulario_transferencia(tareas_df)

elif modulo == "Carga de Estado de Tareas":
    cargar_excel_estado()

elif modulo == "Exportar a Excel":
    tareas_df = mostrar_tareas()
    exportar_excel(tareas_df)

elif modulo == "Calendario de Turnos":
    from modules.calendario import mostrar_calendario_turnos
    mostrar_calendario_turnos()
