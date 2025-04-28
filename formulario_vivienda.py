# app_streamlit.py
import streamlit as st
import pandas as pd
from pathlib import Path
from modulos.data_loader import load_defaults

# Configuración de la página: debe ser lo primero
st.set_page_config(page_title="Dashboard Comparación Apartments", layout="wide")

@st.cache_data
def get_defaults():
    base = Path(__file__).parent
    for path in [base / 'data' / 'default_values.csv', base / 'data' / 'load_defaults.csv', base / 'load_defaults.csv']:
        if path.exists():
            try:
                return load_defaults(path)
            except Exception:
                break
    # Fallback: DataFrame con valores vacíos para cada ítem
    items = [
        "PRECIO", "ESTRATO", "ADMINISTRACION", "PARQUEADERO", "HABITACIONES",
        "ESTUDIO", "CLOSETS", "BAÑOS", "VENTILACION", "REMODELAR", "PISOS",
        "ESCALERAS", "COCINA", "EXTRACTOR", "CENTRO DE ENTRETENIMIENTO",
        "ILUMINACION AHORRADORA", "IMPUESTO PREDIAL", "METRAJE",
        "DISTANCIA TRANSPORTE", "CORTINAS"
    ]
    return pd.DataFrame(
        {col: [''] * len(items) for col in ['Apto Granja', 'Apto Bolivia', 'Comentario']},
        index=items
    )

# Carga inicial de datos y título
df_defaults = get_defaults()
st.title("📊 Dashboard: Comparación Apto Granja vs Apto Bolivia")

# Editor de datos masivo
data_editor_df = df_defaults.reset_index().rename(columns={'index': 'Item'})
try:
    df_edit = st.experimental_data_editor(data_editor_df, num_rows='dynamic')
except AttributeError:
    df_edit = st.data_editor(data_editor_df, num_rows='dynamic')

# Procesar y visualizar
if st.button('Procesar comparación'):
    df_result = df_edit.set_index('Item').reset_index()
    st.subheader('📋 Resultados de la Comparación')
    st.dataframe(df_result, use_container_width=True)

    # Datos numéricos para gráficas
    numeric_df = df_result.set_index('Item')[['Apto Granja', 'Apto Bolivia']]
    numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce')

    # Gráfico comparativo de barras
    st.subheader('📊 Comparativo Numérico')
    st.bar_chart(numeric_df)

    # Gráfico de líneas para comparar series
    st.subheader('📈 Línea Apto Granja vs Apto Bolivia')
    st.line_chart(numeric_df)

    # Gráfico de diferencia absoluta
    diff_series = (numeric_df['Apto Granja'] - numeric_df['Apto Bolivia']).abs()
    st.subheader('📈 Diferencia Absoluta por Ítem')
    st.bar_chart(diff_series)

# Pie de página
st.markdown('---')
st.markdown('*Dashboard generado con Streamlit*')
