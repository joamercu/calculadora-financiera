# indicators.py
import numpy_financial as npf
import pandas as pd
from typing import Dict, Union


def calcular_indicadores(df_amortizacion: pd.DataFrame,
                          tasa_descuento_anual: float) -> Dict[str, Union[float, int, None]]:
    """
    Devuelve un diccionario con:
        - TIR (%)                         : Tasa interna de retorno anualizada
        - VPN ($)                         : Valor presente neto
        - Periodo de Recuperación (meses) : Cuántos meses tarda en recuperar la inversión
        - CET (%)                         : Costo Efectivo Total anual
        - Payback Descontado (meses)      : Tiempo de recuperación con descuento

    Parámetros
    ----------
    df_amortizacion : DataFrame con la tabla de amortización
    tasa_descuento_anual : float  (EA en decimal, p. ej. 0.1095 para 10.95 %)
    """

    # ================================
    # Flujo inicial positivo (monto recibido)
    # ================================
    monto_inicial = df_amortizacion.iloc[0]["Saldo ($)"] + \
                    df_amortizacion.iloc[0]["Amortización ($)"]
    flujos = [monto_inicial] + df_amortizacion["Flujo ($)"].tolist()

    # ================================
    # TIR (tasa interna de retorno)
    # ================================
    try:
        tir_mensual = npf.irr(flujos)
        tir_anual = (1 + tir_mensual) ** 12 - 1 if tir_mensual else None
    except Exception:
        tir_anual = None

    # ================================
    # VPN (valor presente neto)
    # ================================
    tasa_m_desc = tasa_descuento_anual / 12
    try:
        vpn = npf.npv(tasa_m_desc, flujos[1:]) + flujos[0]
    except Exception:
        vpn = None

    # ================================
    # Periodo de recuperación (sin descuento)
    # ================================
    acumulado = 0
    recuperacion = None
    for i, f in enumerate(flujos[1:], start=1):
        acumulado += f
        if acumulado >= 0:
            recuperacion = i
            break

    # ================================
    # CET (Costo Efectivo Total anualizado)
    # ================================
    try:
        cet_mensual = npf.irr(flujos)
        cet_anual = (1 + cet_mensual) ** 12 - 1 if cet_mensual else None
    except Exception:
        cet_anual = None

    # ================================
    # Payback descontado
    # ================================
    acumulado_desc = monto_inicial
    payback_desc = None
    for i, f in enumerate(flujos[1:], 1):
        f_desc = f / ((1 + tasa_m_desc) ** i)
        acumulado_desc += f_desc
        if acumulado_desc >= 0:
            payback_desc = i
            break

    # ================================
    # Resultado
    # ================================
    return {
        "TIR (%)": round(tir_anual * 100, 2) if tir_anual else None,
        "VPN ($)": round(vpn, 2) if vpn is not None else None,
        "Periodo de Recuperación (meses)": recuperacion,
        "CET (%)": round(cet_anual * 100, 2) if cet_anual else None,
        "Payback Descontado (meses)": payback_desc
    }
