import streamlit as st
import pandas as pd
import os

from modules.raptor_module import RAPTOR


UPLOAD_DIR = "uploaded_files"
STATE_FILE = "file_state.csv"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

def save_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        with st.spinner(f'Saving {uploaded_file.name}...'):
            file_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            st.success(f"Pohranjena datoteka: {uploaded_file.name}")
        update_state_file(uploaded_file.name, False)

def update_state_file(file_name, is_used):
    print("Updating state file...")
    if os.path.exists(STATE_FILE):
        df = pd.read_csv(STATE_FILE)
    else:
        df = pd.DataFrame(columns=["Naziv datoteke", "is_used"])

    if file_name not in df["Naziv datoteke"].values:
        new_row = pd.DataFrame({"Naziv datoteke": [file_name], "is_used": [is_used]})
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv(STATE_FILE, index=False)
    
    st.session_state["files_changed"] = False

def load_state_file():
    if os.path.exists(STATE_FILE):
        return pd.read_csv(STATE_FILE)
    else:
        return pd.DataFrame(columns=["Naziv datoteke", "is_used"])

def list_uploaded_files():
    files = load_state_file()
    if files.empty:
        st.write("Prazno! 😔")
    else:
        edited_df = st.data_editor(data=files,
                                   num_rows="dynamic",
                                   key="files",
                                   column_config={
            "Naziv datoteke": {},
            "is_used": {"selector_type": "boolean"}
        }, 
        width=700, 
        height=300,
        disabled=["Naziv datoteke"]
        )
        save_state_changes(edited_df)

def save_state_changes(edited_df):
    print(st.session_state['files'])
    
    if st.session_state['files']['edited_rows'] or st.session_state['files']['deleted_rows']:
        st.session_state["files_changed"] = False
    
    edited_df.to_csv(STATE_FILE, index=False)

st.title("📚Skripte")
st.write("Ovde možeš učitati skripte ili druge datoteke koje želiš podijeliti samnom kako bi ti pomogao u učenju.")
st.write("Jednom kad učitaš skripte, bolje ću razumijeti gradivo kolegija koje me pitaš i ponudit ću ti kvalitetnije odgovore 🤖")
st.write("Učitane datoteke će biti pohranjene na ovom serveru i bit će dostupne samo tebi. Naravno, možeš ih obrisati kad god poželiš.")

uploaded_file = st.file_uploader(label="Učitaj datoteke, prezentacije, skripte, štogod!", type=None, accept_multiple_files=False, help="Učitavanjem datoteka ovdje EduBot dobiva novo znanje i može vam pomoći u razumijevanju skripte/gradiva koji vam nije jasan.")

if uploaded_file is not None:
    save_uploaded_file(uploaded_file)

st.header("Pohranjene datoteke")
list_uploaded_files()

if "files_changed" not in st.session_state:
    st.session_state["files_changed"] = True

if st.button("Opameti me! 🧠", disabled=st.session_state['files_changed']):
    velociraptor = RAPTOR(file_path="./uploaded_files", collection_name="pjs")
