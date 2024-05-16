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

try:
    name, authentication_status, username = authenticator.login(fields={'Form name': 'Prijava', 'Username': 'Korisničko ime', 'Password': 'Lozinka', 'Login': 'Prijavi se'}, location='main')
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    
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