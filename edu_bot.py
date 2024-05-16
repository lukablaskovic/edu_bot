import yaml
import streamlit as st
import streamlit_shadcn_ui as ui

from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import (LoginError)
import os
import pymupdf

st.set_page_config(
        page_title="EduBot",
)

st.title('🤖🎓EduBot')

with open('./config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['pre-authorized']
)

# Add button to toggle between login and registration
if 'view' not in st.session_state:
    st.session_state['view'] = 'login'

if st.session_state['view'] == 'login':
    if st.button("Prvi put si ovdje?"):
        st.session_state['view'] = 'register'
        st.rerun() 
else:
    if st.button("Povratak na prijavu"):
        st.session_state['view'] = 'login'
        st.rerun() 

if st.session_state['view'] == 'login':
    try:
        name, authentication_status, username = authenticator.login(fields={'Form name': 'Prijava', 'Username': 'Korisničko ime', 'Password': 'Lozinka', 'Login': 'Prijavi se'}, location='main')
    except LoginError as e:
        st.error(e)

    if st.session_state["authentication_status"]:
        # User is authenticated
        st.write(f'Hej *{st.session_state["name"]}*')
        st.write('Uspješna prijava. Huuray! 🎉')
        st.write("> Ipak, prije nego nastaviš, molim unesi svoj OpenAI API ključ. Ako ga nemaš, možeš ga dobiti na [OpenAI](https://platform.openai.com/signup).")

        # Set OpenAI API key via sidebar
        openai_api_key = st.sidebar.text_input("OpenAI API ključ", type="password")
        authenticator.logout("Odjava")
        if not openai_api_key:
            st.error("Greška: Nemam OpenAI API ključ.")
            st.stop()

        os.environ['OPENAI_API_KEY'] = openai_api_key

    elif st.session_state["authentication_status"] is False:
        st.error('Korisničko ime/lozinka nisu ispravni. Molimo pokušajte ponovo.')
    elif st.session_state["authentication_status"] is None:
        st.warning('Molimo unesite korisničko ime i lozinku.')

elif st.session_state['view'] == 'register':
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False, fields={'Name': 'Ime i prezime', 'Form name': 'Registracija', 'Username': 'Korisničko ime', 'Password':'Lozinka', 'Repeat password': 'Ponovi lozinku', 'Register': 'Registriraj se!'})
        if email_of_registered_user:
            st.success('User registered successfully')
            
            with open('./config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
