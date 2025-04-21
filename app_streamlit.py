import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import logging
from io import StringIO
import numpy_financial as npf
import numpy as np

from modules.inputs import leer_escenarios_desde_excel
from modules.amortization import generar_tabla_amortizacion
from modules.exporter import exportar_excel

from modules.pdf_generator import generar_pdf_resumen
from modules.pdf_merge import fusionar_pdfs
from modules.indicators import calcular_indicadores

# ---------- CONFIG BÁSICA ---------- #
st.set_page_config(page_title="Simulador Financiero", layout="wide")
st.title("🏡 Simulador Financiero Hipotecario 💜MALE💜 Y JOSE ")






# Logger para modo debug
buffer  = StringIO()
handler = logging.StreamHandler(buffer)
logger  = logging.getLogger("simulador")
logger.handlers = [handler]
logger.setLevel(logging.INFO)

# ---------- SIDEBAR ---------- #
st.sidebar.header("🧮 Parámetros de la Simulación")
r_EA   = st.sidebar.number_input("Tasa Efectiva Anual (%)", value=10.95, step=0.01)


# 👉 NUEVO: costo de oportunidad
costo_oport_EA = st.sidebar.number_input(
    "Costo de oportunidad EA (%)", value=10.50, step=0.1,
    help="Rendimiento neto que obtendrías en la mejor alternativa de riesgo similar"
)
tasa_descuento = st.sidebar.number_input(
    "Costo de oportunidad (%)", value=10.0, step=0.1
) / 100

# Tasa nominal mensual informativa (no editable)
r_TNM  = ((1 + r_EA/100) ** (1/12) - 1) * 100
st.sidebar.number_input("Tasa Nominal Mensual (%)", value=round(r_TNM, 4),
                        step=0.0001, disabled=True)

n_cuotas       = st.sidebar.number_input("Número de cuotas", value=120, step=1)

valor_prestamo = st.sidebar.number_input("Valor del préstamo ($)", value=145_000_000, step=1_000_000)
st.sidebar.caption(f"💰 {valor_prestamo:,.0f}".replace(",", ".") + " COP")




seguro_total = st.sidebar.number_input("Costo total del seguro ($)", value=6_000_000, step=100_000)
st.sidebar.caption(f"🛡️ {seguro_total:,.0f}".replace(",", ".") + " COP")

efec_propios = st.sidebar.number_input("Nuestro efectivo actual ($)", value=160_000_000, step=1_000_000)
st.sidebar.caption(f"🏦 {efec_propios:,.0f}".replace(",", ".") + " COP")

# Cálculo automático del valor total del inmueble
valor_inmueble = valor_prestamo + efec_propios

st.sidebar.caption(f"🏘️ Valor estimado del inmueble: {valor_inmueble:,.0f} COP".replace(",", "."))

# Cálculo del porcentaje del préstamo sobre el valor del inmueble
porcentaje_apalancamiento = (efec_propios / valor_inmueble) * 100
st.sidebar.caption(f"📊 El apalancamiento representa el **{porcentaje_apalancamiento:.2f}%** del valor del inmueble.")

if valor_inmueble > 0:
    porcentaje_prestamo = (valor_prestamo / valor_inmueble) * 100
    st.sidebar.caption(f"📊 El prestmo representa el **{porcentaje_prestamo:.2f}%** del valor del inmueble.")
else:
    st.sidebar.caption("⚠️ Ingresa un valor de inmueble válido para calcular el porcentaje.")



# ---------- APORTES ANTICIPADOS ---------- #
with st.sidebar.expander("➕ Aportes Anticipados"):
    n_aportes = st.number_input("Número de aportes", min_value=0, max_value=10, value=1, step=1, key="n_aportes")

    aportes = []
    for i in range(n_aportes):
        cols = st.columns(3)
        mes = cols[0].number_input(f"Mes #{i+1}", min_value=1, max_value=n_cuotas, value=i+1, key=f"mes_{i}")
        monto = cols[1].number_input(f"Monto #{i+1} ($)", min_value=0, step=500_000, key=f"monto_{i}")
        modo = cols[2].selectbox(f"Tipo #{i+1}", ["plazo", "cuota"], key=f"modo_{i}")
        if monto > 0:
            aportes.append({"mes": mes, "monto": monto, "modo": modo})



# — FIN NUEVO —


debug   = st.sidebar.checkbox("🪲 Modo Debug", value=False)
archivo = st.file_uploader("Opcional: Subir archivo Excel", type=["xlsx"])
ejecutar_button = st.sidebar.button("📊 Ejecutar Simulación")

# ---------- UTILIDADES ---------- #
def money(x):
    """Devuelve texto en formato $ ###,### o '' si no se puede convertir."""
    try:
        return f"$ {float(x):,.0f}"
    except (ValueError, TypeError):
        return ""

# ---------- APP PRINCIPAL ---------- #



if ejecutar_button:
    # 1) CARGAR ESCENARIOS
    if archivo:
        st.success(f"✅ Archivo cargado: {archivo.name}")
        tmp = "entrada_usuario_temp.xlsx"
        with open(tmp,"wb") as f: f.write(archivo.read())

        escenarios = leer_escenarios_desde_excel(tmp, hoja="Ejemplo_de_datos_de_entrada")
        if not escenarios:
            st.warning("⚠️ No se leyó ningún escenario válido del Excel. Uso escenario manual.")
    else:
        escenarios = []

    # ───────── Escenario manual cuando NO suben Excel ─────────
    if not escenarios:
        esc = {
            "nombre": "Escenario personalizado",
            "monto": valor_prestamo,
            "tasa": r_EA / 100,  # EA en decimal
            "plazo": n_cuotas,
            "seguro": seguro_total / n_cuotas,  # seguro mensual
            "fecha_inicio": pd.to_datetime("2025-05-01").date(),
            "aportes": aportes  # << lista completa
        }
        escenarios = [esc]

    # ③  Detener si no se leyó nada
    if not escenarios:
        st.error("No se encontró ningún escenario válido.")
        st.stop()

    carpeta_out = "informes"
    os.makedirs(carpeta_out, exist_ok=True)
    rutas_pdf = []



    for esc in escenarios:
        st.subheader(f"📄 {esc['nombre']}")

        # ---------- Tabla de amortización ----------
        df = generar_tabla_amortizacion(esc)

        # ---------- Indicadores ----------
        # ---------- Indicadores completos ----------
        indicadores = calcular_indicadores(
            df_amortizacion=df,
            tasa_descuento_anual=costo_oport_EA / 100  # decimal
        )

        indicadores = calcular_indicadores(df, tasa_descuento)

        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("TIR (%)", f"{indicadores['TIR (%)']}%" if indicadores['TIR (%)'] else "N/A")
        c2.metric("VPN ($)", money(indicadores["VPN ($)"]))
        c3.metric("Recuperación (meses)", indicadores["Periodo de Recuperación (meses)"] or "N/A")
        c4.metric("CET (%)", f"{indicadores.get('CET (%)', 'N/A')}%")
        c5.metric("Payback descontado", indicadores.get("Payback Descontado (meses)", "N/A"))


        with st.expander("ℹ️ ¿Qué significan estos indicadores?"):
            st.markdown("""
            - **TIR (%)**: Rentabilidad anual del proyecto. Si es mayor al costo de oportunidad, es rentable.
            - **VPN ($)**: Valor actual de la inversión. Si es positivo, conviene.
            - **Periodo de Recuperación**: Cuántos meses toma recuperar el dinero invertido.
            - **CET (%)**: Costo Efectivo Total del crédito (incluye seguros, etc.).
            - **Payback descontado**: Mes en que recuperas tu dinero teniendo en cuenta el valor en el tiempo.
            """)


        import altair as alt

        st.markdown("## 📊 Comparativa de Saldo con Aporte")

        # Recalcular saldo sin aporte
        esc_sin_aporte = esc.copy()
        esc_sin_aporte["mes_aporte"] = None
        esc_sin_aporte["monto_aporte"] = 0
        df_sin_aporte = generar_tabla_amortizacion(esc_sin_aporte)

        # Crear DataFrame combinado
        df_saldos = df[["Mes", "Saldo ($)"]].copy()

        df_saldos = df_saldos.rename(columns={"Saldo ($)": "Saldo con aporte"})

        # Convertir a formato largo
        df_saldos_long = df_saldos.melt(
            id_vars=["Mes"],
            value_vars=["Saldo con aporte"],
            var_name="Escenario",
            value_name="Saldo"
        )

        # Crear gráfico comparativo
        chart_saldos = alt.Chart(df_saldos_long).mark_line(point=True).encode(
            x=alt.X("Mes:O", title="Mes"),
            y=alt.Y("Saldo:Q", title="Saldo del Crédito ($)", axis=alt.Axis(format="$,.0f")),
            color=alt.Color("Escenario:N", title="Escenario", scale=alt.Scale(
                domain=["Saldo con aporte"],
                range=["#7defa1", "#83c9ff"]
            )),
            tooltip=[
                alt.Tooltip("Mes:O", title="Mes"),
                alt.Tooltip("Escenario:N", title="Tipo de saldo"),
                alt.Tooltip("Saldo:Q", title="Saldo", format="$,.0f")
            ]
        ).properties(
            width=800,
            height=400,
            title="📉 Comparación del Saldo con y sin Aporte Anticipado"
        ).configure_view(
            fill="#0e1117"
        ).configure_axis(
            labelColor="#e6eaf1",
            titleColor="#e6eaf1"
        ).configure_title(
            fontSize=18,
            color="#fafafa",
            anchor="start"
        )

        st.altair_chart(chart_saldos, use_container_width=True)





        # --- Payback period (meses) ---





        # ---------- Validaciones ----------
        if (df["Saldo ($)"] < 0).any():
            st.warning("⚠️ Existen saldos negativos en la proyección.")
        if df.isna().any().any():
            st.error("❌ Se encontraron valores faltantes en la tabla.")

        # ---------- Vista parámetros & pasos ----------
        with st.expander("🔍 Parámetros usados para este escenario"):
            st.json(esc)

        with st.expander("🧮 Cálculos paso a paso (primeros 5 meses)"):
            pasos = []
            for _, fila in df.head(10).iterrows():
                pasos.append({
                    "Mes": fila["Mes"],
                    "Saldo inicial": round(fila["Saldo ($)"] + fila["Amortización ($)"], 2),
                    "Interés": fila["Interés ($)"],
                    "Amortización": fila["Amortización ($)"],
                    "Cuota": fila["Cuota ($)"],
                })
            st.table(pd.DataFrame(pasos))

        # ---------- Mostrar tabla con formato ----------
        # Crear copia para mostrar sin decimales y con redondeo hacia arriba
        df_redondeado = df.copy()

        # Detectar columnas numéricas que deben redondearse (con $ en el nombre o cuotas)
        columnas_a_redondear = [col for col in df.columns if
                                "$" in col or "Cuota Total" in col or "Valor de Cuota" in col]

        # Redondear hacia arriba
        for col in columnas_a_redondear:
            df_redondeado[col] = np.ceil(pd.to_numeric(df_redondeado[col], errors='coerce'))


        # Función para formato sin decimales y con puntos de miles
        def money_sin_decimales(x):
            try:
                return f"$ {int(x):,}".replace(",", ".")
            except:
                return x


        # Mostrar con estilo
        st.dataframe(
            df_redondeado.style.format({col: money_sin_decimales for col in columnas_a_redondear}),
            use_container_width=True
        )

        # ---------- Glosario de columnas ----------
        with st.expander("📘 Glosario de columnas de la tabla"):
            st.markdown("""
        | **Columna**           | **Significado** |
        |------------------------|-----------------|
        | **Mes**                | Número secuencial del mes desde el inicio del crédito. |
        | **Fecha**              | Fecha correspondiente al mes de pago (formato año-mes). |
        | **Cuota ($)**          | Valor mensual que se paga por el crédito, sin incluir el seguro. Calculada como cuota fija bajo sistema COLOMBIANO. |
        | **Interés ($)**        | Porción de la cuota mensual que corresponde al pago de intereses sobre el saldo insoluto del préstamo. |
        | **Amortización ($)**   | Porción de la cuota que efectivamente reduce el capital adeudado (saldo del préstamo). |
        | **Saldo ($)**          | Capital pendiente de pago después de aplicar la amortización del mes. |
        | **Seguro ($)**         | Costo mensual del seguro, dividido entre todos los meses. |
        | **Flujo ($)**          | Salida total mensual de dinero, incluyendo cuota y seguro. Se muestra como valor negativo. |
        | **Cuota Total ($)**    | 🆕 Suma de la cuota mensual más el seguro. Refleja el pago total real. |
        | **Aporte Aplicado**    | Indica si en ese mes se aplicó un abono extraordinario. |
        | **Nueva Cuota ($)**    | Si se recalculó la cuota por un aporte, se muestra aquí. |
            """)

        # ---------- Indicadores visuales ----------

        # ---------- Gráficos ----------

        import altair as alt

        # === Preparar datos para Altair ===
        df_flujo = df[["Mes", "Flujo ($)"]].copy()
        df_flujo["Flujo acumulado"] = df_flujo["Flujo ($)"].cumsum()

        # Identificar punto de recuperación
        df_flujo["Recuperado"] = df_flujo["Flujo acumulado"] >= 0
        primer_mes_recuperado = df_flujo[df_flujo["Recuperado"]].head(1)["Mes"].values
        linea_recuperacion = int(primer_mes_recuperado[0]) if len(primer_mes_recuperado) else None

        # === Gráfico base con puntos ===
        chart = alt.Chart(df_flujo).mark_line(
            point=alt.OverlayMarkDef(filled=True, size=70, color="#ffffff")
        ).encode(
            x=alt.X("Mes:O", title="Mes"),
            y=alt.Y("Flujo acumulado:Q", title="Flujo Acumulado ($)", axis=alt.Axis(format="$,.0f")),
            tooltip=[
                alt.Tooltip("Mes:O", title="Mes"),
                alt.Tooltip("Flujo acumulado:Q", title="Flujo Acumulado", format="$,.0f")
            ]
        )




        # === Línea de recuperación si aplica ===
        if linea_recuperacion:
            linea = alt.Chart(pd.DataFrame({
                "x": [linea_recuperacion],
                "label": [f"Recuperación en mes {linea_recuperacion}"]
            })).mark_rule(color="orange", strokeDash=[4, 4]).encode(
                x="x:O"
            ) + alt.Chart(pd.DataFrame({
                "x": [linea_recuperacion],
                "y": [df_flujo[df_flujo["Mes"] == linea_recuperacion]["Flujo acumulado"].values[0]],
                "label": [f"Recuperación"]
            })).mark_text(align="left", dx=5, dy=-5, color="orange").encode(
                x="x:O",
                y="y:Q",
                text="label:N"
            )
            chart = chart + linea

        # === Estilo final y render en Streamlit ===
        chart = chart.properties(
            width=800,
            height=400,
            title="📈 Evolución del Flujo Acumulado"
        ).configure_view(
            fill="#0e1117"
        ).configure_axis(
            labelColor="#e6eaf1",
            titleColor="#e6eaf1"
        ).configure_title(
            fontSize=18,
            color="#fafafa",
            anchor="start"
        )

        st.altair_chart(chart, use_container_width=True)



        fig, ax = plt.subplots()
        ax.pie([efec_propios, valor_prestamo], labels=["Efectivo", "Préstamo"],
               autopct="%1.1f%%", startangle=90)
        ax.axis('equal')
        st.pyplot(fig)

        # ---------- Exportar a Excel ----------
        fname = esc["nombre"].replace(" ", "_") + ".xlsx"
        path_excel = os.path.join(carpeta_out, fname)
        exportar_excel(
            path_excel, df,
            indicadores,
            esc["nombre"]
        )

        st.download_button("⬇️ Descargar Excel", open(path_excel, "rb").read(),
                           file_name=fname)

    # ---------- Debug ----------
    if debug:
        handler.flush()
        st.expander("📜 Log interno").text(buffer.getvalue())
