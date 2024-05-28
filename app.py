import streamlit as st
import os

from auth import load_config, get_authenticator, login, register_user
from openai_key import get_openai_key
from chatbot import chatbot

st.set_page_config(
    page_title="EduBot",
    page_icon="🤖",
)

st.title('🤖🎓EduBot')

"st/session_state_object:", st.session_state

config = load_config()
authenticator = get_authenticator(config)

if 'view' not in st.session_state:
    st.session_state['view'] = 'login'

name, authentication_status, username = login(authenticator)

if authentication_status:
    st.write(f'Hej *{name}*')
    st.write('Uspješna prijava. Huuray! 🎉')

    authenticator.logout("Odjava")

    openai_api_key = get_openai_key()

    chatbot(openai_api_key)

elif authentication_status is False:
    st.error('Korisničko ime/lozinka nisu ispravni. Molimo pokušajte ponovo.')
elif authentication_status is None:
    st.warning('Molimo unesite korisničko ime i lozinku.')

if not authentication_status:
    if st.session_state['view'] == 'login':
        if st.button("Prvi put si ovdje?"):
            st.session_state['view'] = 'register'
            st.rerun()
    else:
        if st.button("Povratak na prijavu"):
            st.session_state['view'] = 'login'
            st.rerun()

if st.session_state['view'] == 'register':
    register_user(authenticator, config)
