# Archivo: reloj.py
import streamlit as st
from datetime import datetime, timedelta
import pytz
import pandas as pd

from modules.turnos import grupo_activo, FECHA_INICIO_GRUPOS
from modules.grupos import GRUPOS_DETALLE

def mostrar_reloj():
    tz = pytz.timezone("America/Bogota")
    ahora = datetime.now(tz)

    st.metric("🕓 Fecha y hora actual", ahora.strftime("%A, %d de %B de %Y - %H:%M:%S"))

    activos = grupo_activo(ahora)
    st.metric("👷‍♂️ Grupo(s) en turno", ", ".join(activos))

    # Mostrar integrantes actuales en formato tabla
    for grupo in activos:
        st.markdown(f"**👥 {grupo} - Integrantes en turno:**")
        integrantes = GRUPOS_DETALLE.get(grupo, "No definido").split(", ")
        df_integrantes = pd.DataFrame({"Integrantes": integrantes})
        st.table(df_integrantes)

    # Calcular días restantes para grupos activos
    info_turnos = []
    for grupo in activos:
        inicio = FECHA_INICIO_GRUPOS[grupo]
        dias_transcurridos = (ahora - inicio).days % 21
        dias_restantes = 14 - dias_transcurridos if dias_transcurridos < 14 else 0
        info_turnos.append(f"{grupo}: {dias_restantes} días restantes")

    st.metric("⏳ Tiempo restante del turno", " | ".join(info_turnos))

    # Determinar próximo grupo en entrar y mostrar integrantes
    dias_para_entrada = []
    for grupo, inicio in FECHA_INICIO_GRUPOS.items():
        dias_transcurridos = (ahora - inicio).days % 21
        if dias_transcurridos >= 14:
            dias_faltan = 21 - dias_transcurridos
            dias_para_entrada.append((grupo, dias_faltan))
    if dias_para_entrada:
        proximo = sorted(dias_para_entrada, key=lambda x: x[1])[0]
        st.markdown("---")
        st.subheader(f"📅 Próximo grupo en entrar: {proximo[0]} en {proximo[1]} días")
        integrantes_proximo = GRUPOS_DETALLE.get(proximo[0], "No definido").split(", ")
        st.table(pd.DataFrame({"Integrantes": integrantes_proximo}))

    # Mostrar últimas 3 tareas si existe el archivo de tareas
    try:
        df_tareas = pd.read_excel("data/tareas.xlsx")
        st.markdown("---")
        st.subheader("🧾 Últimas 3 tareas registradas")
        st.dataframe(df_tareas.tail(3), use_container_width=True)
    except Exception as e:
        st.info("ℹ️ No se encontraron tareas recientes o el archivo no está disponible.")