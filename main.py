from modules.inputs import leer_escenarios_desde_excel
from modules.amortization import generar_tabla_amortizacion
from modules.indicators import calcular_indicadores
from modules.exporter import exportar_excel
from modules.pdf_generator import generar_pdf_resumen
from modules.pdf_merge import fusionar_pdfs

import os
import pandas as pd

def main():
    ruta_entrada = "entrada_usuario.xlsx"
    carpeta_salida = "informes"
    os.makedirs(carpeta_salida, exist_ok=True)

    escenarios = leer_escenarios_desde_excel(ruta_entrada)
    lista_pdfs = []

    for escenario in escenarios:
        print(f"Procesando: {escenario['nombre']}")
        df_amort = generar_tabla_amortizacion(escenario)
        indicadores = calcular_indicadores(df_amort, tasa_descuento_anual=escenario["tasa"])
        nombre_base = escenario["nombre"].replace(" ", "_")
        ruta_excel = os.path.join(carpeta_salida, f"{nombre_base}.xlsx")
        exportar_excel(ruta_excel, df_amort, indicadores, escenario["nombre"])

        if escenario.get("mes_aporte") is not None:
            columna_cuotas = pd.to_numeric(df_amort["Nueva Cuota ($)"], errors="coerce")
            nueva_cuota = columna_cuotas.max() if not columna_cuotas.isna().all() else None

            resumen_aporte = {
                "Escenario": escenario["nombre"],
                "Mes Aporte": escenario["mes_aporte"],
                "Monto Aporte ($)": escenario["monto_aporte"],
                "Modo Aporte": escenario["modo_aporte"],
                "Nueva Cuota": nueva_cuota,
                "Fecha Aporte": df_amort[df_amort["Mes"] == escenario["mes_aporte"]]["Fecha"].values[0],
                "Reducción Estimada": "Disminución de cuota" if escenario["modo_aporte"] == "cuota" else "Disminución de plazo"
            }

            ruta_pdf = generar_pdf_resumen(resumen_aporte, carpeta_salida)
            lista_pdfs.append(ruta_pdf)

    if lista_pdfs:
        fusionar_pdfs(lista_pdfs, os.path.join(carpeta_salida, "informe_aportes_final.pdf"))
        print("✅ Informe consolidado generado con éxito.")
    else:
        print("No se registraron aportes anticipados, no se generó informe PDF.")

if __name__ == "__main__":
    main()
