import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
import pytz
from modules.grupos import GRUPOS_DETALLE  # importar desde módulo externo

def grupo_activo(fecha_hoy):
    # Definición de turnos rotativos 14x7 desde 2025-01-14
    tz = pytz.timezone("America/Bogota")
    FECHA_INICIO = tz.localize(datetime(2025, 1, 14))
    dias_transcurridos = (fecha_hoy - FECHA_INICIO).days % 28

    activos = []
    if 0 <= dias_transcurridos < 14:
        activos.append("Grupo A")
    if 7 <= dias_transcurridos < 21:
        activos.append("Grupo B")
    if 14 <= dias_transcurridos < 28:
        activos.append("Grupo C")
    if dias_transcurridos >= 21 or dias_transcurridos < 7:
        activos.append("Grupo D")
    return activos

def mostrar_calendario_turnos():
    st.header("📅 Calendario de Turnos (30 días)")

    tz = pytz.timezone("America/Bogota")
    fecha_inicio_usuario = st.date_input("Selecciona la fecha de inicio del mes", datetime.today().replace(day=1))

    if st.button("📆 Calcular calendario"):
        hoy = tz.localize(datetime.combine(fecha_inicio_usuario, datetime.min.time()))
        fechas = [hoy + timedelta(days=i) for i in range(30)]

        tabla = []
        for fecha in fechas:
            activos = grupo_activo(fecha)
            fila = {
                "Fecha": fecha.strftime("%A, %d de %B de %Y").capitalize(),
                "Grupo A": "🛠️" if "Grupo A" in activos else "😴",
                "Grupo B": "🛠️" if "Grupo B" in activos else "😴",
                "Grupo C": "🛠️" if "Grupo C" in activos else "😴",
                "Grupo D": "🛠️" if "Grupo D" in activos else "😴",
            }
            tabla.append(fila)

        df = pd.DataFrame(tabla)

        # Aplicar etiquetas flotantes en los encabezados
        tooltip_headers = {
            "Grupo A": f"🛠️ Grupo A: {GRUPOS_DETALLE['Grupo A']}",
            "Grupo B": f"🛠️ Grupo B: {GRUPOS_DETALLE['Grupo B']}",
            "Grupo C": f"🛠️ Grupo C: {GRUPOS_DETALLE['Grupo C']}",
            "Grupo D": f"🛠️ Grupo D: {GRUPOS_DETALLE['Grupo D']}",
        }

        df.rename(columns=tooltip_headers, inplace=True)

        st.dataframe(df.style.set_properties(**{'text-align': 'center'}), use_container_width=True)
