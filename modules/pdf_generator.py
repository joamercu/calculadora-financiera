from fpdf import FPDF
import os

def generar_pdf_resumen(resumen_aporte: dict, ruta_salida: str) -> str:
    nombre_escenario = resumen_aporte.get("Escenario", "Simulación")
    nombre_archivo = os.path.join(ruta_salida, f"resumen_{nombre_escenario.replace(' ', '_')}.pdf")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, f"Resumen del {nombre_escenario}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    for clave, valor in resumen_aporte.items():
        pdf.cell(60, 10, str(clave) + ":", 0)
        pdf.cell(100, 10, str(valor), 0, ln=True)
    pdf.output(nombre_archivo)
    return nombre_archivo
