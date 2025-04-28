# app_streamlit.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Configuración de la página (única llamada al inicio)
st.set_page_config(
    page_title="Dashboard Comparación Apartamentos",
    layout="wide"
)

# Función única de carga de datos (cacheada)
@st.cache_data
def load_data():
    base = Path(__file__).parent
    for file in [
        base / 'data' / 'default_values.csv',
        base / 'data' / 'load_defaults.csv',
        base / 'load_defaults.csv'
    ]:
        if file.exists():
            try:
                df = pd.read_csv(file)
                if 'Item' in df.columns:
                    df.set_index('Item', inplace=True)
                return df[['Apto Granja', 'Apto Bolivia']]
            except:
                break
    # Fallback con columnas esenciales
    defaults = {
        'PRECIO': {'Apto Granja': 315000000, 'Apto Bolivia': 307000000},
        'ESTRATO': {'Apto Granja': 3, 'Apto Bolivia': 3},
        'ADMINISTRACION': {'Apto Granja': 115000, 'Apto Bolivia': 350000},
        'METRAJE': {'Apto Granja': 78, 'Apto Bolivia': 69}
    }
    return pd.DataFrame.from_dict(defaults, orient='index')

# Helper para editor de datos con fallback
def data_editor(df, **kwargs):
    try:
        return st.experimental_data_editor(df, **kwargs)
    except AttributeError:
        return st.data_editor(df, **kwargs)

# Cargar o recuperar datos en sesión
if 'df_defaults' not in st.session_state:
    st.session_state['df_defaults'] = load_data()

# Obtener DataFrame base
df_defaults = st.session_state['df_defaults']

# Título y descripción
st.title("🏢 Comparación de Apartamentos")
st.markdown("### 📊 Apto Granja vs Apto Bolivia")

# Preparar DataFrame para edición
editor_df = df_defaults.reset_index().rename(columns={'index': 'Item'})

# Ejecutar editor de datos
df_edit = data_editor(editor_df, num_rows='dynamic')

# Validar columna 'Item' antes de indexar
if 'Item' in df_edit.columns:
    df_current = df_edit.set_index('Item')
else:
    st.warning("Columna 'Item' no encontrada; se mantiene índice numérico.")
    df_current = df_edit.copy()

# Métricas esenciales
cols = st.columns(4)
for idx, label in enumerate(['PRECIO', 'METRAJE']):
    try:
        g_val = pd.to_numeric(df_current.loc[label, 'Apto Granja'], errors='coerce')
        b_val = pd.to_numeric(df_current.loc[label, 'Apto Bolivia'], errors='coerce')
    except KeyError:
        g_val = b_val = None
    unit = ' m²' if label == 'METRAJE' else ''
    with cols[idx*2]:
        st.metric(f"{label} Granja", f"{g_val:,.0f}{unit}" if g_val is not None else "N/A")
    with cols[idx*2+1]:
        st.metric(f"{label} Bolivia", f"{b_val:,.0f}{unit}" if b_val is not None else "N/A")

# Pestañas de Datos y Gráficos
tab1, tab2 = st.tabs(["📋 Datos", "📊 Gráficos"])

with tab1:
    st.write(df_current)

with tab2:
    num = df_current.apply(pd.to_numeric, errors='coerce').dropna()
    if not num.empty:
        st.subheader('📊 Comparativo Numérico')
        st.bar_chart(num)
        st.subheader('📈 Diferencia Absoluta')
        diff = (num['Apto Granja'] - num['Apto Bolivia']).abs()
        st.line_chart(diff)
    else:
        st.warning('No hay datos numéricos para graficar')

# Pie de página
st.markdown('---')
st.markdown('*Dashboard generado con Streamlit*')
