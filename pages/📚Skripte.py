import streamlit as st
import streamlit_shadcn_ui as ui
import pandas as pd

import os

UPLOAD_DIR = "uploaded_files"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        with st.spinner(f'Saving {uploaded_file.name}...'):
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Pohranjena datoteka: {uploaded_file.name}")

def list_uploaded_files():
    files = os.listdir(UPLOAD_DIR)
    if not files:
        st.write("Prazno! 😔")
    else:
        data = {
            "Naziv datoteke": files,
            "is_used": [True] * len(files) 
        }
        df = pd.DataFrame(data)
        st.data_editor(data=df,
                       num_rows="dynamic",
                       column_config={
            "Naziv datoteke": {},
            "is_used": {"selector_type": "boolean"}
        }, 
        width=700, 
        height=300,
        disabled=["Naziv datoteke"]
        )

    
st.title("📚Skripte")
st.write("Ovde možeš učitati skripte ili druge datoteke koje želiš podijeliti samnom kako bi ti pomogao u učenju.")
st.write("Jednom kad učitaš skripte, bolje ću razumijeti gradivo kolegija koje me pitaš i ponudit ću ti kvalitetnije odgovore 🤖")
st.write("Učitane datoteke će biti pohranjene na ovom serveru i bit će dostupne samo tebi. Naravno, možeš ih obrisati kad god poželiš.")

uploaded_file = st.file_uploader(label="", type=None, accept_multiple_files=False, help="Učitavanjem datoteka ovdje EduBot dobiva novo znanje i može vam pomoći u razumijevanju skripte/gradiva koji vam nije jasan.")

if uploaded_file is not None:
    save_uploaded_file(uploaded_file)



st.header("Pohranjene datoteke")
list_uploaded_files()
