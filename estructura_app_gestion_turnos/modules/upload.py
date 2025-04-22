# Archivo: upload.py
import streamlit as st
import pandas as pd
import os
from PIL import Image

def cargar_excel_estado():
    st.header("📤 Cargar estado actualizado de tareas")

    archivo = st.file_uploader("Selecciona un archivo Excel (.xlsx)", type=["xlsx"])

    columnas_requeridas = {"ID", "Estado", "% Avance"}

    if archivo is not None:
        try:
            df = pd.read_excel(archivo)
            st.success("✅ Archivo cargado correctamente.")
            st.dataframe(df, use_container_width=True)

            if not columnas_requeridas.issubset(set(df.columns)):
                st.error(f"❌ El archivo debe contener las columnas: {', '.join(columnas_requeridas)}")
                return None

            # Guardar archivo localmente si se desea
            nombre_archivo = f"estado_tareas_{archivo.name}"
            ruta_guardado = os.path.join("data", nombre_archivo)
            with open(ruta_guardado, "wb") as f:
                f.write(archivo.getbuffer())

            # Botón para aplicar cambios
            if st.button("📥 Aplicar cambios a tareas"):
                tareas_path = "data/tareas.xlsx"
                if os.path.exists(tareas_path):
                    df_tareas = pd.read_excel(tareas_path)

                    # Aplicar actualizaciones por ID
                    for i, row in df.iterrows():
                        idx = df_tareas[df_tareas["ID"] == row["ID"]].index
                        if not idx.empty:
                            for campo in ["Estado", "% Avance"]:
                                if campo in df.columns:
                                    df_tareas.loc[idx, campo] = row[campo]

                    df_tareas.to_excel(tareas_path, index=False)
                    st.success("✅ Tareas actualizadas correctamente.")
                else:
                    st.error("❌ No se encontró el archivo de tareas.")

            return df

        except Exception as e:
            st.error(f"❌ Error al leer el archivo: {e}")

    return None

def cargar_fotos_referencia():
    st.header("📸 Subir imágenes de referencia de la tarea")

    imagenes = st.file_uploader(
        "Carga hasta 3 imágenes",
        type=["jpg", "jpeg", "png"],
        accept_multiple_files=True
    )

    fotos_guardadas = []

    if imagenes:
        os.makedirs("data/fotos", exist_ok=True)

        for i, img in enumerate(imagenes[:3]):
            ruta = os.path.join("data", "fotos", img.name)
            with open(ruta, "wb") as f:
                f.write(img.getbuffer())
            fotos_guardadas.append(ruta)

            st.image(Image.open(ruta), caption=f"Imagen {i+1}", use_column_width=True)

    return fotos_guardadas
