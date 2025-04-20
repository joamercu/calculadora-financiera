# indicators.py
import numpy_financial as npf
import pandas as pd
from typing import Dict

def calcular_indicadores(df_amortizacion: pd.DataFrame,
                          tasa_descuento_anual: float) -> Dict[str, float]:
    """
    Devuelve un diccionario con:
        - TIR (%)  : Tasa interna de retorno anualizada
        - VPN ($)  : Valor presente neto
        - Periodo de Recuperación (meses)

    Parámetros
    ----------
    df_amortizacion : DataFrame con la tabla de amortización
    tasa_descuento_anual : float  (EA en decimal, p. ej. 0.1095 para 10.95 %)
    """
    # --- Flujo inicial positivo (monto del préstamo) ---
    monto_inicial = df_amortizacion.iloc[0]["Saldo ($)"] + \
                    df_amortizacion.iloc[0]["Amortización ($)"]

    flujos = [monto_inicial] + df_amortizacion["Flujo ($)"].tolist()

    # --- TIR (irr) ---
    tir_m = npf.irr(flujos)          # mensual
    tir_a = (1 + tir_m) ** 12 - 1 if tir_m is not None else None

    # --- VPN ---
    tasa_m_desc = tasa_descuento_anual / 12
    vpn = npf.npv(tasa_m_desc, flujos[1:]) + flujos[0]

    # --- Periodo de recuperación ---
    acumulado = 0
    recuperacion = None
    for i, f in enumerate(flujos[1:], start=1):
        acumulado += f
        if acumulado >= 0:
            recuperacion = i
            break

    return {
        "TIR (%)": None if tir_a is None else round(tir_a * 100, 2),
        "VPN ($)": round(vpn, 2),
        "Periodo de Recuperación (meses)": recuperacion
    }
