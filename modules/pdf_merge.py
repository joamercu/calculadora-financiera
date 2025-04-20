from fpdf import FPDF
from PyPDF2 import PdfMerger
from datetime import datetime
import os

def crear_portada(nombre_usuario: str, lista_escenarios: list, archivo_salida: str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Informe Consolidado de Aportes Anticipados", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    fecha = datetime.today().strftime('%Y-%m-%d')
    pdf.cell(0, 10, f"Fecha: {fecha}", ln=True, align='C')
    pdf.cell(0, 10, f"Responsable: {nombre_usuario}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Tabla de Contenidos", ln=True)
    pdf.set_font("Arial", '', 12)
    for i, nombre in enumerate(lista_escenarios, start=1):
        pdf.cell(0, 8, f"{i}. {nombre} ....................... pág. {i+1}", ln=True)
    pdf.output(archivo_salida)

def fusionar_pdfs(rutas_pdfs: list, salida: str, nombre_usuario: str = None):
    if nombre_usuario is None:
        nombre_usuario = input("Ingrese el nombre del responsable del análisis: ")
    escenarios = [os.path.splitext(os.path.basename(r))[0].replace("resumen_", "").replace("_", " ") for r in rutas_pdfs]
    portada_temp = "portada_temp.pdf"
    crear_portada(nombre_usuario, escenarios, portada_temp)
    merger = PdfMerger()
    merger.append(portada_temp)
    for ruta, nombre in zip(rutas_pdfs, escenarios):
        merger.append(ruta, outline_item=nombre)
    merger.write(salida)
    merger.close()
    os.remove(portada_temp)
