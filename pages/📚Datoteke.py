import streamlit as st
import pandas as pd
import os
from openai_key import get_openai_key
import time
from modules.raptor_module import get_raptor

from settings import initialize_settings

st.set_page_config(
    page_title="EduBot - Datoteke",
    page_icon="🤖",
)

if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = get_openai_key()

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
    if os.path.exists(STATE_FILE):
        df = pd.read_csv(STATE_FILE)
    else:
        df = pd.DataFrame(columns=["Naziv datoteke", "is_used"])

    if file_name not in df["Naziv datoteke"].values:
        new_row = pd.DataFrame({"Naziv datoteke": [file_name], "is_used": [is_used]})
        df = pd.concat([df, new_row], ignore_index=True)
    else:
        df.loc[df["Naziv datoteke"] == file_name, "is_used"] = is_used

    df.to_csv(STATE_FILE, index=False)
    st.session_state["files_changed"] = True

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
        disabled=["Naziv datoteke"],
        on_change=on_files_changed
        )
        if "original_files" not in st.session_state:
            st.session_state["original_files"] = files.copy()

        return edited_df


def on_files_changed():
    st.session_state["files_changed"] = True
    st.session_state["saved_files_config"] = False
    

def save_state_changes(edited_df):
    edited_df.to_csv(STATE_FILE, index=False)

if st.session_state['connected']:
    initialize_settings()

    st.title("📚Datoteke")
    st.write("Ovde možeš učitati skripte ili druge datoteke koje želiš podijeliti samnom kako bi ti pomogao u učenju.")
    st.write("Jednom kad učitaš skripte, bolje ću razumijevati gradivo kolegija koje me pitaš i ponudit ću ti kvalitetnije odgovore 🤖")
    st.write("Učitane datoteke će biti pohranjene na ovom serveru i bit će dostupne samo tebi. Naravno, možeš ih obrisati kad god poželiš.")

    uploaded_file = st.file_uploader(label="Učitaj datoteke, prezentacije, skripte, štogod!", type=None, accept_multiple_files=False, help="Učitavanjem datoteka ovdje EduBot dobiva novo znanje i može vam pomoći u razumijevanju skripte/gradiva koji vam nije jasan.")

    if uploaded_file is not None:
        save_uploaded_file(uploaded_file)

    st.header("Učitane datoteke")
    edited_df = list_uploaded_files()

    if "files_changed" not in st.session_state:
        st.session_state["files_changed"] = False

    if "saved_files_config" not in st.session_state:
        st.session_state["saved_files_config"] = False

    if st.session_state["files_changed"]:
        if st.button("Spremi promjene", type= 'primary'):
            save_state_changes(edited_df)
            st.session_state["original_files"] = edited_df.copy()
            st.success("Promjene su spremljene!")
            st.session_state["saved_files_config"] = True
            st.session_state["disabled"] = False

    if st.session_state["files_changed"] and not st.session_state["saved_files_config"]:
        st.session_state["disabled"] = True

    elif not st.session_state["files_changed"] and not st.session_state["saved_files_config"]:
        st.session_state["disabled"] = False

    if st.button("Opameti me! 🧠", type='secondary', disabled=st.session_state.get("disabled", True)):
        with st.spinner('Učim iz tvojih datoteka...'):
            used_files = edited_df.loc[edited_df["is_used"] == True, "Naziv datoteke"].tolist()
            used_files = [os.path.join(UPLOAD_DIR, file) for file in used_files] 
            st.session_state["raptor"] = get_raptor(files=used_files, force_rebuild=True)
        st.success("EduBot je sada pametniji!🔥")
        st.session_state["files_changed"] = False

else:
    st.error("Moraš biti prijavljen za ovo!")