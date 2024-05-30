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
    st.sidebar.markdown("# Korisnički profil")
    st.sidebar.markdown(f"👤 {st.session_state['user_info'].get('name')}")
    
    with st.form(key="profile_form"):
        st.text_input("Ime i prezime", value=st.session_state['user_info'].get('name'), disabled=True)
        st.text_input("Email",  value=st.session_state['user_info'].get('email'), disabled=True)
        st.selectbox("Godina studija", ["1. prijediplomski", "2. prijediplomski", "3. prijediplomski", "1. diplomski", "2. diplomski"], key="study_year")

        st.form_submit_button("Ažuriraj")


else:
    st.error("Moraš biti prijavljen za ovo!")
