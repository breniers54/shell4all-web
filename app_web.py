import streamlit as st
import pandas as pd
import json
import os
import subprocess
from fpdf import FPDF

# Configuration de la page
st.set_page_config(page_title="Shell4All Web", page_icon="🛡️", layout="wide")

DB_FILE = "shell_data.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"Système": {"dir": "Liste les fichiers"}}

def save_data(data):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

data = load_data()

st.title("🛡️ Shell4All - Version Web")

# Barre latérale pour ajouter des commandes
with st.sidebar:
    st.header("➕ Ajouter une commande")
    new_cat = st.text_input("Catégorie")
    new_cmd = st.text_input("Commande")
    new_desc = st.text_area("Description")
    if st.button("Enregistrer"):
        if new_cat and new_cmd:
            if new_cat not in data: data[new_cat] = {}
            data[new_cat][new_cmd] = new_desc
            save_data(data)
            st.success("Ajouté !")
            st.rerun()

# Affichage des commandes
st.subheader("📚 Ma Bibliothèque")
for cat, cmds in data.items():
    with st.expander(f"📁 {cat}"):
        for cmd, desc in cmds.items():
            col1, col2, col3 = st.columns([2, 4, 1])
            col1.code(cmd)
            col2.write(desc)
            if col3.button("▶️", key=f"run_{cmd}"):
                # Exécution (uniquement si hébergé localement)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                st.text_area("Résultat :", value=result.stdout + result.stderr, height=100)

# Export PDF
if st.button("📄 Générer le guide PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Mon Guide de Commandes", ln=True, align='C')
    for cat, cmds in data.items():
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, cat, ln=True)
        for cmd, desc in cmds.items():
            pdf.set_font("Arial", '', 10)
            pdf.write(5, f"- {cmd} : {desc}\n")
    
    pdf_name = "mon_guide.pdf"
    pdf.output(pdf_name)
    with open(pdf_name, "rb") as f:
        st.download_button("⬇️ Télécharger le PDF", f, file_name=pdf_name)