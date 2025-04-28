# app_streamlit.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path

# Configuración de la página: debe ser lo primero
st.set_page_config(
    page_title="Dashboard Comparación Apartamentos", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Función para cargar datos
@st.cache_data
def load_defaults(csv_path):
    df = pd.read_csv(csv_path)
    if 'Item' in df.columns:
        df = df.set_index('Item')
    return df

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

# Función para formatear valores
def format_value(val):
    if isinstance(val, (int, float)) and not np.isnan(val):
        if val > 1000000:  # Millones
            return f"${val/1000000:.1f}M"
        elif val > 1000:  # Miles
            return f"${val/1000:.1f}K"
        else:
            return f"${val:,.0f}"
    return val

# Función para iconizar valores booleanos
def iconize(val):
    if str(val).upper() in ['SI', 'YES', 'TRUE', '1']:
        return '✅'
    elif str(val).upper() in ['NO', 'FALSE', '0']:
        return '❌'
    return val

# Función para resaltar diferencias
def highlight_diff(row):
    styles = ['', '', '']
    try:
        # Intentar convertir a números
        v1 = pd.to_numeric(row['Apto Granja'], errors='coerce')
        v2 = pd.to_numeric(row['Apto Bolivia'], errors='coerce')

        if not pd.isna(v1) and not pd.isna(v2):
            if v1 > v2:
                styles = ['background-color: #d4f4dd', 'background-color: #f9d6d5', '']
            elif v1 < v2:
                styles = ['background-color: #f9d6d5', 'background-color: #d4f4dd', '']
    except:
        # Si no son números, comparar como texto
        if row['Apto Granja'] == 'SI' and row['Apto Bolivia'] == 'NO':
            styles = ['background-color: #d4f4dd', 'background-color: #f9d6d5', '']
        elif row['Apto Granja'] == 'NO' and row['Apto Bolivia'] == 'SI':
            styles = ['background-color: #f9d6d5', 'background-color: #d4f4dd', '']

    return styles

# Carga inicial de datos
df_defaults = get_defaults()

# Título y descripción
st.title("🏢 Comparación de Apartamentos")
st.markdown("### 📊 Apto Granja vs Apto Bolivia")

# Tarjetas de resumen
try:
    precio_granja = pd.to_numeric(df_defaults.loc['PRECIO', 'Apto Granja'], errors='coerce')
    precio_bolivia = pd.to_numeric(df_defaults.loc['PRECIO', 'Apto Bolivia'], errors='coerce')
    metraje_granja = pd.to_numeric(df_defaults.loc['METRAJE', 'Apto Granja'], errors='coerce')
    metraje_bolivia = pd.to_numeric(df_defaults.loc['METRAJE', 'Apto Bolivia'], errors='coerce')

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("💰 Precio Granja", f"${precio_granja:,.0f}" if not pd.isna(precio_granja) else "N/A")
    with col2:
        st.metric("💰 Precio Bolivia", f"${precio_bolivia:,.0f}" if not pd.isna(precio_bolivia) else "N/A")
    with col3:
        st.metric("📏 Metraje Granja", f"{metraje_granja} m²" if not pd.isna(metraje_granja) else "N/A")
    with col4:
        st.metric("📏 Metraje Bolivia", f"{metraje_bolivia} m²" if not pd.isna(metraje_bolivia) else "N/A")

    # Diferencia de precio
    if not pd.isna(precio_granja) and not pd.isna(precio_bolivia):
        diff = precio_granja - precio_bolivia
        if diff > 0:
            st.info(f"💡 Apto Bolivia es más económico por ${abs(diff):,.0f}")
        elif diff < 0:
            st.info(f"💡 Apto Granja es más económico por ${abs(diff):,.0f}")
except:
    st.warning("No se pudieron calcular las métricas de resumen")

# Tabs para organizar el contenido
tab1, tab2, tab3 = st.tabs(["📋 Datos", "📊 Gráficos", "📝 Análisis"])

with tab1:
    # Editor de datos
    st.subheader("Editar Datos de Comparación")
    data_editor_df = df_defaults.reset_index().rename(columns={'index': 'Item'})
    try:
        df_edit = st.experimental_data_editor(data_editor_df, num_rows='dynamic')
    except AttributeError:
        df_edit = st.data_editor(data_editor_df, num_rows='dynamic')

    # Botón para procesar
    if st.button('Procesar comparación', key='process_btn'):
        df_result = df_edit.set_index('Item').reset_index()

        # Tabla estilizada
        st.subheader('📋 Resultados de la Comparación')
        styled = df_result.style.apply(highlight_diff, axis=1, subset=['Apto Granja', 'Apto Bolivia', 'Comentario'])
        st.dataframe(styled, use_container_width=True)

        # Guardar en sesión para otras pestañas
        st.session_state['df_result'] = df_result

with tab2:
    st.subheader("Visualización Gráfica")

    if 'df_result' in st.session_state:
        df_result = st.session_state['df_result']

        # Preparar datos numéricos
        numeric_df = df_result.set_index('Item')[['Apto Granja', 'Apto Bolivia']]
        numeric_df = numeric_df.apply(pd.to_numeric, errors='coerce').dropna()

        if not numeric_df.empty:
            # Gráfico de barras con Plotly
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=numeric_df.index,
                y=numeric_df['Apto Granja'],
                name='Apto Granja',
                marker_color='#4CAF50'
            ))
            fig.add_trace(go.Bar(
                x=numeric_df.index,
                y=numeric_df['Apto Bolivia'],
                name='Apto Bolivia',
                marker_color='#FF5722'
            ))
            fig.update_layout(
                title='Comparativo Numérico',
                xaxis_title='Características',
                yaxis_title='Valor',
                barmode='group',
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)

            # Gráfico de radar para comparación multidimensional
            if len(numeric_df) >= 3:  # Necesitamos al menos 3 dimensiones
                categories = numeric_df.index.tolist()
                fig_radar = go.Figure()

                # Normalizar valores para el radar
                max_vals = numeric_df.max()
                norm_df = numeric_df.div(max_vals)

                fig_radar.add_trace(go.Scatterpolar(
                    r=norm_df['Apto Granja'].values.tolist(),
                    theta=categories,
                    fill='toself',
                    name='Apto Granja'
                ))
                fig_radar.add_trace(go.Scatterpolar(
                    r=norm_df['Apto Bolivia'].values.tolist(),
                    theta=categories,
                    fill='toself',
                    name='Apto Bolivia'
                ))

                fig_radar.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                        )
                    ),
                    showlegend=True,
                    title='Comparación Multidimensional (Normalizada)',
                    height=600
                )
                st.plotly_chart(fig_radar, use_container_width=True)

            # Gráfico de diferencia
            diff_series = (numeric_df['Apto Granja'] - numeric_df['Apto Bolivia'])
            colors = ['#4CAF50' if x > 0 else '#FF5722' for x in diff_series]

            fig_diff = go.Figure()
            fig_diff.add_trace(go.Bar(
                x=diff_series.index,
                y=diff_series.values,
                marker_color=colors,
                name='Diferencia'
            ))
            fig_diff.update_layout(
                title='Diferencia (Apto Granja - Apto Bolivia)',
                xaxis_title='Características',
                yaxis_title='Diferencia',
                height=400
            )
            st.plotly_chart(fig_diff, use_container_width=True)
        else:
            st.warning("No hay datos numéricos para visualizar")
    else:
        st.info("Procesa la comparación en la pestaña 'Datos' para ver los gráficos")

with tab3:
    st.subheader("Análisis Comparativo")

    if 'df_result' in st.session_state:
        df_result = st.session_state['df_result']

        # Análisis automático
        st.markdown("### 🔍 Análisis Automático")

        # Convertir a numérico donde sea posible
        df_numeric = df_result.copy()
        for col in ['Apto Granja', 'Apto Bolivia']:
            df_numeric[col] = pd.to_numeric(df_numeric[col], errors='coerce')

        # Análisis de precio
        try:
            precio_g = df_numeric.loc[df_numeric['Item'] == 'PRECIO', 'Apto Granja'].values[0]
            precio_b = df_numeric.loc[df_numeric['Item'] == 'PRECIO', 'Apto Bolivia'].values[0]

            if not pd.isna(precio_g) and not pd.isna(precio_b):
                diff_precio = precio_g - precio_b
                if diff_precio > 0:
                    st.markdown(f"- **Precio**: Apto Bolivia es ${abs(diff_precio):,.0f} más económico")
                else:
                    st.markdown(f"- **Precio**: Apto Granja es ${abs(diff_precio):,.0f} más económico")
        except:
            pass

        # Análisis de metraje
        try:
            metraje_g = df_numeric.loc[df_numeric['Item'] == 'METRAJE', 'Apto Granja'].values[0]
            metraje_b = df_numeric.loc[df_numeric['Item'] == 'METRAJE', 'Apto Bolivia'].values[0]

            if not pd.isna(metraje_g) and not pd.isna(metraje_b):
                diff_metraje = metraje_g - metraje_b
                if diff_metraje > 0:
                    st.markdown(f"- **Metraje**: Apto Granja es {abs(diff_metraje)} m² más grande")
                else:
                    st.markdown(f"- **Metraje**: Apto Bolivia es {abs(diff_metraje)} m² más grande")

                # Precio por m²
                if not pd.isna(precio_g) and not pd.isna(precio_b):
                    precio_m2_g = precio_g / metraje_g
                    precio_m2_b = precio_b / metraje_b

                    st.markdown(f"- **Precio por m²**: Apto Granja: ${precio_m2_g:,.0f}/m² | Apto Bolivia: ${precio_m2_b:,.0f}/m²")

                    if precio_m2_g < precio_m2_b:
                        st.markdown(f"  - Apto Granja tiene mejor relación precio/m² (${precio_m2_g:,.0f} vs ${precio_m2_b:,.0f})")
                    else:
                        st.markdown(f"  - Apto Bolivia tiene mejor relación precio/m² (${precio_m2_b:,.0f} vs ${precio_m2_g:,.0f})")
        except:
            pass

        # Análisis de administración
        try:
            admin_g = df_numeric.loc[df_numeric['Item'] == 'ADMINISTRACION', 'Apto Granja'].values[0]
            admin_b = df_numeric.loc[df_numeric['Item'] == 'ADMINISTRACION', 'Apto Bolivia'].values[0]

            if not pd.isna(admin_g) and not pd.isna(admin_b):
                diff_admin = admin_g - admin_b
                if diff_admin < 0:
                    st.markdown(f"- **Administración**: Apto Granja tiene cuota ${abs(diff_admin):,.0f} menor")
                else:
                    st.markdown(f"- **Administración**: Apto Bolivia tiene cuota ${abs(diff_admin):,.0f} menor")
        except:
            pass

        # Análisis de características booleanas
        bool_items = ['PARQUEADERO', 'VENTILACION', 'REMODELAR', 'EXTRACTOR', 'CENTRO DE ENTRETENIMIENTO']
        ventajas_g = []
        ventajas_b = []

        for item in bool_items:
            try:
                val_g = str(df_result.loc[df_result['Item'] == item, 'Apto Granja'].values[0]).upper()
                val_b = str(df_result.loc[df_result['Item'] == item, 'Apto Bolivia'].values[0]).upper()

                if val_g in ['SI', 'YES', 'TRUE', '1'] and val_b in ['NO', 'FALSE', '0']:
                    ventajas_g.append(item.lower())
                elif val_b in ['SI', 'YES', 'TRUE', '1'] and val_g in ['NO', 'FALSE', '0']:
                    ventajas_b.append(item.lower())
            except:
                pass

        if ventajas_g:
            st.markdown(f"- **Ventajas Apto Granja**: {', '.join(ventajas_g)}")
        if ventajas_b:
            st.markdown(f"- **Ventajas Apto Bolivia**: {', '.join(ventajas_b)}")

        # Resumen final
        st.markdown("### 📝 Resumen")
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Apto Granja")
            st.markdown("**Pros:**")
            pros_g = []
            if 'precio_g' in locals() and 'precio_b' in locals() and precio_g < precio_b:
                pros_g.append(f"Más económico (${precio_g:,.0f} vs ${precio_b:,.0f})")
            if 'metraje_g' in locals() and 'metraje_b' in locals() and metraje_g > metraje_b:
                pros_g.append(f"Mayor metraje ({metraje_g} m² vs {metraje_b} m²)")
            if 'precio_m2_g' in locals() and 'precio_m2_b' in locals() and precio_m2_g < precio_m2_b:
                pros_g.append(f"Mejor relación precio/m² (${precio_m2_g:,.0f}/m²)")
            if 'admin_g' in locals() and 'admin_b' in locals() and admin_g < admin_b:
                pros_g.append(f"Menor cuota de administración (${admin_g:,.0f})")
            for v in ventajas_g:
                pros_g.append(f"Tiene {v}")

            if pros_g:
                for p in pros_g:
                    st.markdown(f"- {p}")
            else:
                st.markdown("- No se identificaron ventajas claras")

        with col2:
            st.markdown("#### Apto Bolivia")
            st.markdown("**Pros:**")
            pros_b = []
            if 'precio_g' in locals() and 'precio_b' in locals() and precio_b < precio_g:
                pros_b.append(f"Más económico (${precio_b:,.0f} vs ${precio_g:,.0f})")
            if 'metraje_g' in locals() and 'metraje_b' in locals() and metraje_b > metraje_g:
                pros_b.append(f"Mayor metraje ({metraje_b} m² vs {metraje_g} m²)")
            if 'precio_m2_g' in locals() and 'precio_m2_b' in locals() and precio_m2_b < precio_m2_g:
                pros_b.append(f"Mejor relación precio/m² (${precio_m2_b:,.0f}/m²)")
            if 'admin_g' in locals() and 'admin_b' in locals() and admin_b < admin_g:
                pros_b.append(f"Menor cuota de administración (${admin_b:,.0f})")
            for v in ventajas_b:
                pros_b.append(f"Tiene {v}")

            if pros_b:
                for p in pros_b:
                    st.markdown(f"- {p}")
            else:
                st.markdown("- No se identificaron ventajas claras")
    else:
        st.info("Procesa la comparación en la pestaña 'Datos' para ver el análisis")

# Pie de página
st.markdown("---")
st.markdown("*Dashboard generado con Streamlit — Análisis de Propiedades*")
