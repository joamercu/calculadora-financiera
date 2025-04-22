# Archivo: turnos.py
import pandas as pd
from datetime import datetime, timedelta
import pytz
import locale

from modules.grupos import GRUPOS_DETALLE

# Establecer localización en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

# Zona horaria para Colombia
tz = pytz.timezone('America/Bogota')

# Fecha de inicio de turnos por grupo (puedes modificar esta fecha si cambia el ciclo)
FECHA_INICIO_GRUPOS = {
    "Grupo A": tz.localize(datetime(2025, 1, 14)),
    "Grupo B": tz.localize(datetime(2025, 1, 21)),
    "Grupo C": tz.localize(datetime(2025, 1, 28)),
    "Grupo D": tz.localize(datetime(2025, 2, 4))
}

GRUPOS = list(FECHA_INICIO_GRUPOS.keys())

# Cada grupo trabaja 14 días y descansa 7 (ciclo de 21 días)
def grupo_activo(fecha_hoy):
    activos = []
    for grupo, fecha_inicio in FECHA_INICIO_GRUPOS.items():
        dias_transcurridos = (fecha_hoy - fecha_inicio).days
        if dias_transcurridos >= 0:
            ciclo_dia = dias_transcurridos % 21
            if ciclo_dia < 14:
                activos.append(grupo)
    return activos

def generar_tabla_turnos(desde, hasta):
    fechas = pd.date_range(desde, hasta)
    data = []
    for fecha in fechas:
        fecha_local = tz.localize(datetime.combine(fecha, datetime.min.time()))
        activos = grupo_activo(fecha_local)
        row = {g: ("🛠️" if g in activos else "😴") for g in GRUPOS}
        row["Fecha"] = fecha_local.strftime("%A, %d de %B de %Y").capitalize()
        data.append(row)

    df = pd.DataFrame(data)
    columnas = ["Fecha"] + GRUPOS
    df = df[columnas]

    return df.style.set_table_styles(
        [{'selector': 'th', 'props': [('text-align', 'center')]},
         {'selector': 'td', 'props': [('text-align', 'center')]}]
    ).set_properties(
        subset=GRUPOS + ["Fecha"],
        **{"white-space": "normal", "word-wrap": "break-word"}
    )
