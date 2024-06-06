import streamlit as st
import os
from dotenv import load_dotenv
from streamlit_google_auth import Authenticate
from sqlalchemy import MetaData, Table, insert

from modules.sqlrag_module import create_users_table, get_engine, upsert_user, get_user_by_email

st.set_page_config(
    page_title="EdubBot - Korisnički profil",
    page_icon="🤖",
)

load_dotenv()

authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name='edubot_cookie',
    cookie_key=os.getenv('COOKIE_KEY'),
    cookie_expiry_days=30,
    redirect_uri='http://localhost:8501',
)

authenticator.check_authentification()

create_users_table()

email = st.session_state['user_info'].get('email')
user_details = get_user_by_email(email) 

if st.session_state['connected']:
    st.title('👤Korisnički profil')
    st.markdown(f'Hej {st.session_state["user_info"].get("name")} 👋')
    st.markdown('Ovdje možeš ažurirati neke svoje osobne podatke.')

    study_year = user_details.get('study_year') if user_details else "1. prijediplomski"
    about_me = user_details.get('about_me') if user_details else ""
    programming_knowledge = user_details.get('programming_knowledge') if user_details else 0

    with st.form(key="profile_form"):
        name = st.text_input("Ime i prezime", value=st.session_state['user_info'].get('name'), disabled=True)
        email = st.text_input("Email", value=st.session_state['user_info'].get('email'), disabled=True)
        study_year = st.selectbox("Godina studija", ["1. prijediplomski", "2. prijediplomski", "3. prijediplomski", "1. diplomski", "2. diplomski"], index=["1. prijediplomski", "2. prijediplomski", "3. prijediplomski", "1. diplomski", "2. diplomski"].index(study_year), key="study_year")
        about_me = st.text_area("O meni", value=about_me, key="about_me", help="Opiši mi kakav si student i na koji način najbolje učiš.")
        programming_knowledge = st.slider("Znanje iz programiranja",
                                          min_value=0,
                                          max_value=10,
                                          value=programming_knowledge,
                                          key="programming_knowledge",
                                          help="Ocijeni svoje znanje iz programiranja od 0 do 10. Ovisno o tvojem znanju koje ovdje navedeš, prilagodit ću svoje odgovore. [0] - nemam pojma, apsolutni početnik sam, [10] - mogu napisati svoj programski jezik")
        submit_button = st.form_submit_button("Ažuriraj", type="primary")

        if submit_button:
            user_info = {
                "name": name,
                "email": email,
                "study_year": study_year,
                "about_me": about_me,
                "programming_knowledge": programming_knowledge
            }
            upsert_user(user_info)  
            st.success("Podaci su uspješno ažurirani!")

else:
    st.error("Moraš biti prijavljen za ovo!")
