
import streamlit as st
from fpdf import FPDF
import matplotlib.pyplot as plt
import os
from io import BytesIO

st.set_page_config(page_title="Cortes de Aluminio", layout="centered")

st.title("🪓 Calculadora de Cortes de Aluminio con PDF")
st.markdown("Ingresá los datos para calcular el peso, costo y distribución de cortes.")

# Entradas generales
precio_kg = st.number_input("Precio del kg de aluminio ($)", min_value=0.0, step=0.01)
codigo_perfil = st.text_input("Código del perfil")
peso_metro = st.number_input("Peso del perfil (kg/m)", min_value=0.0, step=0.01)

largo_barra_m = st.number_input("Largo de barra (máx. 6.20 m)", min_value=0.0, step=0.01)
if largo_barra_m > 6.20:
    st.error("⚠️ SUPERA LARGO DE BARRA")
largo_barra_mm = largo_barra_m * 1000

# Carga de cortes
st.markdown("### Cortes")
cortes = []
num_cortes = st.number_input("Cantidad de tipos de corte", min_value=1, step=1)

for i in range(num_cortes):
    st.markdown(f"**Corte #{i+1}**")
    medida = st.number_input(f"Medida (mm) del corte #{i+1}", min_value=1.0, step=1.0, key=f"medida{i}")
    ajuste = st.radio(f"¿Tiene ajuste en el corte #{i+1}?", ("No", "Sumar", "Restar"), key=f"ajuste{i}")
    if ajuste != "No":
        valor_ajuste = st.number_input("Cantidad a ajustar (mm)", min_value=0.0, step=1.0, key=f"ajuste_valor{i}")
        medida += valor_ajuste if ajuste == "Sumar" else -valor_ajuste
    cantidad = st.number_input(f"Cantidad de cortes de {medida:.1f} mm", min_value=1, step=1, key=f"cant{i}")
    cortes.extend([medida] * int(cantidad))

if st.button("Generar PDF"):
    cortes.sort(reverse=True)
    disponible = largo_barra_mm
    barras = []
    retazos = []

    todos_cortes = cortes.copy()
    while todos_cortes:
        disponible = largo_barra_mm
        barra = []
        for medida in todos_cortes[:]:
            if medida <= disponible:
                barra.append(medida)
                disponible -= medida
                todos_cortes.remove(medida)
        barras.append(barra)
        retazos.append(disponible)

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Perfil: {codigo_perfil}", ln=True)

    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Precio por kilo: ${precio_kg}", ln=True)
    pdf.cell(0, 10, f"Peso por metro: {peso_metro} kg/m", ln=True)
    pdf.cell(0, 10, f"Largo de barra: {largo_barra_m:.2f} m", ln=True)
    pdf.cell(0, 10, f"Barras necesarias: {len(barras)}", ln=True)

    peso_total = 0
    costo_total = 0

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Cortes útiles:", ln=True)
    pdf.set_font("Arial", '', 11)

    for barra in barras:
        for medida in barra:
            peso = (medida / 1000) * peso_metro
            costo = peso * precio_kg
            peso_total += peso
            costo_total += costo
            pdf.cell(0, 8, f"- {medida:.1f} mm -> {peso:.3f} kg - ${costo:.2f}", ln=True)

    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Retazos:", ln=True)
    pdf.set_font("Arial", '', 11)
    for ret_mm in retazos:
        peso = (ret_mm / 1000) * peso_metro
        costo = peso * precio_kg
        tipo = "UTILIZABLE" if ret_mm >= 1000 else "SCRAP"
        pdf.cell(0, 8, f"- {ret_mm:.1f} mm -> {peso:.3f} kg - ${costo:.2f} [{tipo}]", ln=True)

    # Anexo 7%
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Anexo 7%:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(0, 10, f"Costo con 7% adicional: ${costo_total * 1.07:.2f}", ln=True)

    # Exportar PDF
    pdf_bytes = pdf.output(dest='S').encode('latin1')
st.download_button(
    label="📄 Descargar PDF",
    data=pdf_bytes,
    file_name="cortes_aluminio.pdf",
    mime="application/pdf"
)
