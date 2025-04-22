# Archivo: modules/turnos.py
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Zona horaria para Colombia
tz = pytz.timezone('America/Bogota')

# Fecha de inicio de ciclo por grupo (14 días trabajo, 7 días descanso)
FECHA_INICIO_GRUPOS = {
    'Grupo A': tz.localize(datetime(2025, 4, 30)),
    'Grupo B': tz.localize(datetime(2025, 4, 10)),
    'Grupo C': tz.localize(datetime(2025, 4, 7)),
    'Grupo D': tz.localize(datetime(2025, 4, 4)),
}
GRUPOS = list(FECHA_INICIO_GRUPOS.keys())

# Diccionarios para formateo manual de fecha en español
MESES_ES = [
    "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"
]
DIAS_ES = [
    "lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"
]

def formatear_fecha_es(fecha: datetime) -> str:
    dia_semana = DIAS_ES[fecha.weekday()]
    dia = fecha.day
    mes = MESES_ES[fecha.month - 1]
    anio = fecha.year
    return f"{dia_semana}, {dia} de {mes} de {anio}"

def grupo_activo(fecha_hoy):
    """
    Devuelve lista de tuplas (grupo, estado, días_restantes) con ciclo 14/7 días.
    """
    estados = []
    for grupo, inicio in FECHA_INICIO_GRUPOS.items():
        dias = (fecha_hoy - inicio).days
        if dias >= 0:
            ciclo = dias % 21
            if ciclo < 14:
                estado = 'trabajo'
                dias_rest = 14 - ciclo
            else:
                estado = 'descanso'
                dias_rest = 21 - ciclo
            estados.append((grupo, estado, dias_rest))
    return estados

def generar_tabla_turnos(desde: datetime, hasta: datetime):
    """
    Genera tabla estilizada de turnos con emoticones y texto centrado.
    """
    fechas = pd.date_range(desde, hasta)
    data = []
    for fecha in fechas:
        fecha_local = tz.localize(datetime.combine(fecha, datetime.min.time()))
        estados = grupo_activo(fecha_local)
        fila = { 'Fecha': formatear_fecha_es(fecha_local) }
        for grupo, estado, dias_rest in estados:
            icon = '🛠️' if estado == 'trabajo' else '😴'
            fila[grupo] = f"{icon} {estado.capitalize()} ({dias_rest})"
        # Asegurar columnas para todos los grupos
        for g in GRUPOS:
            fila.setdefault(g, '')
        data.append(fila)

    df = pd.DataFrame(data)[['Fecha'] + GRUPOS]
    styler = df.style.set_properties(**{
        'text-align': 'center',
        'white-space': 'normal',
        'word-wrap': 'break-word'
    }).hide_index()
    return styler
