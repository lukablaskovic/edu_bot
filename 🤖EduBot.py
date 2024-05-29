import streamlit as st
import os

from streamlit_google_auth import Authenticate
from openai_key import get_openai_key
from chatbot import chatbot
from dotenv import load_dotenv

#import logging
#logging.basicConfig(level=logging.DEBUG)

load_dotenv()

st.set_page_config(
    page_title="EduBot",
    page_icon="🤖",
)

st.title('🤖🎓EduBot')


#"st.session_state", st.session_state

authenticator = Authenticate(
    secret_credentials_path = 'google_credentials.json',
    cookie_name='edubot_cookie',
    cookie_key=os.getenv('COOKIE_KEY'),
    cookie_expiry_days=30,
    redirect_uri = 'http://localhost:8501',
)

# Catch the login event
authenticator.check_authentification()


if st.session_state['connected']:
    #st.image(st.session_state['user_info'].get('picture'))
    st.write(f"Hej, {st.session_state['user_info'].get('name')}👋🏻")
    st.write("Uspješna prijava! Huuray! 🎉")
    st.write("""Tu sam da ti olakšam tvoju studentsku avanturu na Fakultetu informatike. Mogu ti pomoći s pitanjima o studiju, predmetima, profesorima, projektima i još mnogo toga. Pitaj me što god želiš! 🤖🎓""")

    openai_api_key = get_openai_key()

    with st.sidebar:
        if st.button('Odjava'):
            authenticator.logout()
        
    chatbot(openai_api_key)

else:
    st.write("Bok👋🏻 Kako bi mogao koristiti EduBot, moraš se prijaviti.")
    
    authenticator.login(justify_content="start")
    
    
    