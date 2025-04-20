import pandas as pd
import streamlit as st
from typing import Optional, List, Dict

def leer_escenarios_desde_excel(
    ruta_excel: str,
    hoja: Optional[str] = None
) -> List[Dict]:
    # 1) Abrir libro y decidir hoja
    try:
        xls = pd.ExcelFile(ruta_excel)
    except Exception as e:
        st.error(f"❌ No pude abrir el archivo: {e}")
        return []
    hojas = xls.sheet_names
    if hoja in hojas:
        hoja_a_leer = hoja
    else:
        if hoja:
            st.warning(f"⚠️ Hoja «{hoja}» no existe; usando «{hojas[0]}»")
        hoja_a_leer = hojas[0]

    # 2) Leer DataFrame completo como strings
    try:
        df = pd.read_excel(xls, sheet_name=hoja_a_leer, dtype=str)
    except Exception as e:
        st.error(f"❌ Error al leer la hoja «{hoja_a_leer}»: {e}")
        return []

    # 3) Normalizar encabezados
    df.columns = df.columns.str.strip().str.lower()

    # 4) Mapear posibles nombres de columna a nombres internos
    columnas = {
        "nombre":           "nombre",
        "escenario":        "nombre",
        "monto":            "monto",
        "tasa":             "tasa",
        "tasa (%)":         "tasa",
        "plazo":            "plazo",
        "seguro":           "seguro",
        "fecha inicio":     "fecha_inicio",
        "fecha":            "fecha_inicio",
        "mes aporte":       "mes_aporte",
        "monto aporte":     "monto_aporte",
        "modo aporte":      "modo_aporte",
        "tipo reduccion":   "modo_aporte",
    }
    df = df.rename(columns={k: v for k, v in columnas.items() if k in df.columns})

    # 5) Validar que existan las columnas mínimas
    requeridas = {"nombre","monto","tasa","plazo","seguro","fecha_inicio"}
    if not requeridas.issubset(df.columns):
        faltan = requeridas - set(df.columns)
        st.error("❌ Faltan columnas: " + ", ".join(faltan))
        return []

    # 6) Construir la lista de escenarios
    escenarios: List[Dict] = []
    for i, row in df.iterrows():
        try:
            # Extraer aportes múltiples si existen
            aportes = []
            for j in range(1, 11):
                mes_col = f"mes_aporte_{j}"
                monto_col = f"monto_aporte_{j}"
                modo_col = f"modo_aporte_{j}"

                if mes_col in row and monto_col in row:
                    try:
                        mes = int(float(row[mes_col]))
                        monto = float(row[monto_col])
                        modo = str(row.get(modo_col, "plazo")).strip().lower()
                        if mes > 0 and monto > 0:
                            aportes.append({"mes": mes, "monto": monto, "modo": modo})
                    except Exception:
                        continue

            # Si no hay lista múltiple, usar aporte único (retrocompatibilidad)
            if not aportes and not pd.isna(row.get("mes_aporte")):
                aportes.append({
                    "mes": int(float(row["mes_aporte"])),
                    "monto": float(row.get("monto_aporte", 0)),
                    "modo": str(row.get("modo_aporte", "plazo")).strip().lower()
                })

            # Validaciones
            meses = [a["mes"] for a in aportes]
            if len(meses) != len(set(meses)):
                st.warning(f"Fila {i + 2}: Meses de aporte duplicados en el escenario «{row['nombre']}».")
            for a in aportes:
                if a["monto"] > float(row["monto"]):
                    st.warning(
                        f"Fila {i + 2}: El aporte de ${a['monto']:,.0f} excede el monto del préstamo en «{row['nombre']}».")

            esc = {
                "nombre": str(row["nombre"]).strip(),
                "monto": float(row["monto"]),
                "tasa": float(row["tasa"]),
                "plazo": int(float(row["plazo"])),
                "seguro": float(row["seguro"]),
                "fecha_inicio": pd.to_datetime(row["fecha_inicio"]).date(),
                "aportes": aportes
            }
            escenarios.append(esc)
        except Exception as e:
            st.warning(f"Fila {i + 2}: {e}")

    if not escenarios:
        st.error("No se encontró ningún escenario válido.")
    return escenarios

