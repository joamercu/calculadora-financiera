# app_streamlit.py
import streamlit as st
import pandas as pd
from pathlib import Path

# Configuración de la página (primero)
st.set_page_config(
    page_title="Dashboard Comparación Apartamentos",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Carga de defaults
def load_defaults():
    base = Path(__file__).parent
    for path in [base/'data'/'default_values.csv', base/'data'/'load_defaults.csv', base/'load_defaults.csv']:
        if path.exists():
            try:
                df = pd.read_csv(path)
                if 'Item' in df.columns:
                    df = df.set_index('Item')
                return df
            except:
                break
    # Fallback estático
    defaults = {
        'PRECIO': {'Apto Granja': 315000000, 'Apto Bolivia': 307000000},
        'ESTRATO': {'Apto Granja': 3, 'Apto Bolivia': 3},
        'ADMINISTRACION': {'Apto Granja': 115000, 'Apto Bolivia': 350000},
        'PARQUEADERO': {'Apto Granja': 'SI', 'Apto Bolivia': 'SI'},
        'HABITACIONES': {'Apto Granja': 3, 'Apto Bolivia': 3},
        'ESTUDIO': {'Apto Granja': 1, 'Apto Bolivia': 0},
        'CLOSETS': {'Apto Granja': 'En 2 habitaciones', 'Apto Bolivia': 'SI'},
        'BAÑOS': {'Apto Granja': 2, 'Apto Bolivia': 2},
        'VENTILACION': {'Apto Granja': 'NO', 'Apto Bolivia': 'SI'},
        'REQUIERE REMODELAR': {'Apto Granja': 'SI', 'Apto Bolivia': 'NO'},
        'PISOS': {'Apto Granja': 1, 'Apto Bolivia': 4},
        'ESCALERAS': {'Apto Granja': 'SI', 'Apto Bolivia': 'SI'},
        'COCINA': {'Apto Granja': 'SI', 'Apto Bolivia': 'SI'},
        'EXTRACTOR': {'Apto Granja': 'NO', 'Apto Bolivia': 'SI'},
        'CENTRO DE ENTRETENIMIENTO': {'Apto Granja': 'NO', 'Apto Bolivia': 'SI'},
        'ILUMINACION AHORRADORA': {'Apto Granja': 'SI', 'Apto Bolivia': 'NO'},
        'IMPUESTO PREDIAL': {'Apto Granja': 500000, 'Apto Bolivia': 450000},
        'METRAJE': {'Apto Granja': 78, 'Apto Bolivia': 69},
        'DISTANCIA TRANSPORTE': {'Apto Granja': 11, 'Apto Bolivia': 23},
        'CORTINAS': {'Apto Granja': 'SI', 'Apto Bolivia': 'SI'}
    }
    return pd.DataFrame.from_dict(defaults, orient='index')

# Datos iniciales
df_defaults = load_defaults()

# Título y descripción
st.title("🏢 Comparación de Apartamentos")
st.markdown("### 📊 Apto Granja vs Apto Bolivia")

# Edición masiva de datos
data_editor_df = df_defaults.reset_index().rename(columns={'index':'Item'})
try:
    df_edit = st.experimental_data_editor(data_editor_df, num_rows='dynamic')
except AttributeError:
    df_edit = st.data_editor(data_editor_df, num_rows='dynamic')

# Convertir edición en DataFrame indexado
df_current = df_edit.set_index('Item')

# Métricas resumen
t1, t2, t3, t4 = st.columns(4)
precio_g = pd.to_numeric(df_current.loc['PRECIO','Apto Granja'], errors='coerce')
precio_b = pd.to_numeric(df_current.loc['PRECIO','Apto Bolivia'], errors='coerce')
met_g = pd.to_numeric(df_current.loc['METRAJE','Apto Granja'], errors='coerce')
met_b = pd.to_numeric(df_current.loc['METRAJE','Apto Bolivia'], errors='coerce')
with t1: st.metric("💰 Precio Granja", f"${precio_g:,.0f}" if not pd.isna(precio_g) else "N/A")
with t2: st.metric("💰 Precio Bolivia", f"${precio_b:,.0f}" if not pd.isna(precio_b) else "N/A")
with t3: st.metric("📏 Metraje Granja", f"{met_g} m²" if not pd.isna(met_g) else "N/A")
with t4: st.metric("📏 Metraje Bolivia", f"{met_b} m²" if not pd.isna(met_b) else "N/A")

# Info diferencia precio
if not pd.isna(precio_g) and not pd.isna(precio_b):
    diff = precio_g - precio_b
    if diff>0: st.info(f"💡 Bolivia más económico por ${abs(diff):,.0f}")
    elif diff<0: st.info(f"💡 Granja más económico por ${abs(diff):,.0f}")

# Visualizaciones
tab1, tab2 = st.tabs(["📋 Datos","📊 Gráficos"])

with tab1:
    st.write(df_current)

with tab2:
    # Datos numéricos
    num = df_current[['Apto Granja','Apto Bolivia']].apply(pd.to_numeric, errors='coerce').dropna()
    if not num.empty:
        st.subheader('📊 Comparativo Numérico')
        st.bar_chart(num)
        st.subheader('📈 Línea Comparativa')
        st.line_chart(num)
        diff = (num['Apto Granja']-num['Apto Bolivia']).abs()
        st.subheader('📈 Diferencia Absoluta')
        st.bar_chart(diff)
    else:
        st.warning('No hay datos numéricos para graficar')

# Pie de página
st.markdown('---')
st.markdown('*Dashboard generado con Streamlit*')
