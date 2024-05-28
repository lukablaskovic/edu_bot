import yaml
import streamlit as st
import streamlit_shadcn_ui as ui

from yaml.loader import SafeLoader
import streamlit_authenticator as stauth
from streamlit_authenticator.utilities.exceptions import LoginError
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

st.set_page_config(
        page_title="EduBot",
        page_icon="🤖",

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

try:
    name, authentication_status, username = authenticator.login(fields={'Form name': 'Prijava', 'Username': 'Korisničko ime', 'Password': 'Lozinka', 'Login': 'Prijavi se'}, location='main')
except LoginError as e:
    st.error(e)

if st.session_state["authentication_status"]:
    # User is authenticated
    st.write(f'Hej *{st.session_state["name"]}*')
    st.write('Uspješna prijava. Huuray! 🎉')

    # Checkbox to read OpenAI API key from environment
    use_env_key = st.sidebar.checkbox("Učitaj OpenAI API ključ iz okruženja")

    if use_env_key:
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            st.error("Greška: OpenAI API ključ nije postavljen u okruženju.")
            st.write("> Molim te postavi svoj OpenAI API ključ u .env datoteku ili unesi ključ ručno.")
            st.stop()
        else:
            st.sidebar.write("OpenAI API ključ učitan iz okruženja.")
    else:
        openai_api_key = st.sidebar.text_input("OpenAI API ključ", type="password")
        if not openai_api_key:
            st.error("Greška: Nemam OpenAI API ključ.")
            st.write("> Ipak, prije nego nastaviš, molim unesi svoj OpenAI API ključ. Ako ga nemaš, možeš ga dobiti na [OpenAI](https://platform.openai.com/signup).")
            st.stop()

    os.environ['OPENAI_API_KEY'] = openai_api_key

    authenticator.logout("Odjava")

elif st.session_state["authentication_status"] is False:
    st.error('Korisničko ime/lozinka nisu ispravni. Molimo pokušajte ponovo.')
elif st.session_state["authentication_status"] is None:
    st.warning('Molimo unesite korisničko ime i lozinku.')

if not st.session_state["authentication_status"]:
    if st.session_state['view'] == 'login':
        if st.button("Prvi put si ovdje?"):
            st.session_state['view'] = 'register'
            st.rerun()
    else:
        if st.button("Povratak na prijavu"):
            st.session_state['view'] = 'login'
            st.rerun()

if st.session_state['view'] == 'register':
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(pre_authorization=False, fields={'Name': 'Ime i prezime', 'Form name': 'Registracija', 'Username': 'Korisničko ime', 'Password':'Lozinka', 'Repeat password': 'Ponovi lozinku', 'Register': 'Registriraj se!'})
        if email_of_registered_user:
            st.success('User registered successfully')
            
            with open('./config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
