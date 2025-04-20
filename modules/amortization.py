import pandas as pd
from datetime import timedelta

def generar_tabla_amortizacion(parametros: dict) -> pd.DataFrame:
    monto         = parametros["monto"]
    tasa_anual    = parametros["tasa"]        # EA en decimal, p.ej. 0.1095
    plazo         = parametros["plazo"]
    seguro        = parametros["seguro"]
    fecha_inicio  = parametros["fecha_inicio"]

    # Retrocompatibilidad: convertir aporte único a lista
    if "aportes" not in parametros:
        mes_aporte = parametros.get("mes_aporte")
        monto_aporte = parametros.get("monto_aporte", 0)
        modo_aporte = parametros.get("modo_aporte", "plazo")
        if mes_aporte is not None and monto_aporte:
            parametros["aportes"] = [{"mes": mes_aporte, "monto": monto_aporte, "modo": modo_aporte}]

    aportes = sorted(parametros.get("aportes", []), key=lambda a: a["mes"])



    # → Aquí la corrección clave:
    tasa_mensual = (1 + tasa_anual) ** (1/12) - 1

    # Cuota PMT con tasa mensual
    cuota = monto * (tasa_mensual * (1 + tasa_mensual)**plazo) \
            / ((1 + tasa_mensual)**plazo - 1)

    saldo       = monto
    tabla       = []
    idx_aporte = 0


    # ✅ Variables con respaldo por si no existen en el diccionario
    mes_aporte = parametros.get("mes_aporte")
    monto_aporte = parametros.get("monto_aporte", 0)
    modo_aporte = parametros.get("modo_aporte", "plazo")
    aporte_aplicado = False

    for mes in range(1, plazo + 1):
        fecha = fecha_inicio + timedelta(days=30 * (mes - 1))

        # Si el saldo ya fue pagado, la cuota va a 0 pero el seguro sigue cobrándose
        if saldo <= 0:
            fila = {
                "Mes": mes,
                "Fecha": fecha.strftime("%Y-%m"),
                "Cuota ($)": 0.0,
                "Interés ($)": 0.0,
                "Amortización ($)": 0.0,
                "Saldo ($)": 0.0,
                "Seguro ($)": round(seguro, 2),
                "Flujo ($)": round(-seguro, 2),
                "Aporte Aplicado": "",
                "Aporte ($)": 0.0,
                "Nueva Cuota ($)": ""
            }
            tabla.append(fila)
            continue

        interes = saldo * tasa_mensual
        amortizacion = cuota - interes

        # Inicializar acumulador del aporte a plazo
        aporte_plazo_mes = 0

        # Aplicar todos los aportes en este mes
        aportes_mes = [a for a in aportes if a["mes"] == mes]
        for aporte in aportes_mes:
            saldo -= aporte["monto"]
            if aporte["modo"] == "cuota":
                cuotas_restantes = plazo - mes
                if cuotas_restantes > 0:
                    cuota = saldo * (tasa_mensual * (1 + tasa_mensual) ** cuotas_restantes) \
                            / ((1 + tasa_mensual) ** cuotas_restantes - 1)
            else:
                aporte_plazo_mes += aporte["monto"]

        saldo -= amortizacion
        saldo = max(saldo, 0)  # evitar saldo negativo

        # Actualizar flujo incluyendo aporte tipo plazo
        flujo = -(cuota + seguro + aporte_plazo_mes)


        fila = {
            "Mes": mes,
            "Fecha": fecha.strftime("%Y-%m"),
            "Cuota ($)": round(cuota, 2),
            "Interés ($)": round(interes, 2),
            "Amortización ($)": round(amortizacion, 2),
            "Saldo ($)": round(saldo, 2),
            "Seguro ($)": round(seguro, 2),
            "Flujo ($)": round(flujo, 2),
            "Aporte Aplicado": "Sí" if aportes_mes else "",
            "Aporte ($)": sum(a["monto"] for a in aportes_mes) if aportes_mes else "",
            "Nueva Cuota ($)": round(cuota, 2) if any(a["modo"] == "cuota" for a in aportes_mes) else "",

        }
        tabla.append(fila)

    df = pd.DataFrame(tabla)

    # Calcular meses ahorrados si el crédito termina antes del plazo original
    ultimo_mes_util = df[df["Saldo ($)"] > 0]["Mes"].max()
    if pd.notna(ultimo_mes_util):
        df["Meses ahorrados"] = [plazo - ultimo_mes_util] * len(df)
    else:
        df["Meses ahorrados"] = 0

    return df
