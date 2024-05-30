import streamlit as st
import os
from dotenv import load_dotenv
from streamlit_google_auth import Authenticate
st.set_page_config(
    page_title="Korisnički profil",
    page_icon="👤",
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


if st.session_state['connected']:
    st.title('👤Korisnički profil')
    st.markdown(f'Hej {st.session_state["user_info"].get("name")} 👋')
    st.markdown('Ovdje možeš ažurirati neke svoje osobne podatke. ')

    
    with st.form(key="profile_form"):
        st.text_input("Ime i prezime", value=st.session_state['user_info'].get('name'), disabled=True)
        st.text_input("Email",  value=st.session_state['user_info'].get('email'), disabled=True)
        st.selectbox("Godina studija", ["1. prijediplomski", "2. prijediplomski", "3. prijediplomski", "1. diplomski", "2. diplomski"], key="study_year")
        st.text_area("O meni", key="about_me", help="Opiši mi kakav si student i na koji način najbolje učiš.")
        st.slider("Znanje iz programiranja", min_value=0, max_value=10, key="programming_knowledge", help="Ocijeni svoje znanje iz programiranja od 0 do 10.")
        st.form_submit_button("Ažuriraj")


else:
    st.error("Moraš biti prijavljen za ovo!")
