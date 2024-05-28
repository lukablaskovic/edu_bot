import yaml
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
from streamlit_authenticator.utilities.exceptions import LoginError

def load_config():
    with open('./config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
    return config

def get_authenticator(config):
    return stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        config['pre-authorized']
    )

def login(authenticator):
    try:
        name, authentication_status, username = authenticator.login(
            fields={'Form name': 'Prijava', 'Username': 'Korisničko ime', 'Password': 'Lozinka', 'Login': 'Prijavi se'}, 
            location='main'
        )
        return name, authentication_status, username
    except LoginError as e:
        st.error(e)
        return None, None, None

def register_user(authenticator, config):
    try:
        email_of_registered_user, username_of_registered_user, name_of_registered_user = authenticator.register_user(
            pre_authorization=False, 
            fields={'Name': 'Ime i prezime', 'Form name': 'Registracija', 'Username': 'Korisničko ime', 'Password':'Lozinka', 'Repeat password': 'Ponovi lozinku', 'Register': 'Registriraj se!'}
        )
        if email_of_registered_user:
            st.success('User registered successfully')
            with open('./config.yaml', 'w') as file:
                yaml.dump(config, file, default_flow_style=False)
    except Exception as e:
        st.error(e)
