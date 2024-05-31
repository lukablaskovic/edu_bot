import streamlit as st
import os

from streamlit_google_auth import Authenticate
from openai_key import get_openai_key
from chatbot import render_chatbot
from dotenv import load_dotenv



# Import logging
# logging.basicConfig(level=logging.DEBUG)



st.set_page_config(
    page_title="EduBot",
    page_icon="🤖",
)
load_dotenv()
st.title('🤖🎓EduBot')

st.sidebar.title('🤖🎓EduBot')
st.sidebar.write("Chatbot za personalizaciju nastavnih materijala")

st.sidebar.write("Autor: [Luka Blašković](https://github.com/lukablaskovic)")

st.sidebar.write("Source kod dostupan [ovdje](https://github.com/lukablaskovic/edu_bot).")

#"st.session_state", st.session_state

authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name='edubot_cookie',
    cookie_key=os.getenv('COOKIE_KEY'),
    cookie_expiry_days=30,
    redirect_uri='http://localhost:8501',
)

authenticator.check_authentification()

if st.session_state['connected']:

    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"Hej, {st.session_state['user_info'].get('name')}👋🏻")
        st.write("Uspješna prijava! Huuray! 🎉")
        st.write("""Tu sam da ti olakšam tvoju studentsku avanturu na Fakultetu informatike. Mogu ti pomoći s pitanjima o studiju, predmetima, profesorima, projektima i još mnogo toga. """)
        st.write("Nije ti jasan silabus iz nekog kolegija, neki zadatak iz skripte, ili te pak zanima koliko ti nedostaje bodova za prolaz i što moraš sve dovršiti za taj projekt iz Programskog🔥")

    with col2:
        debug_mode_on = st.toggle("Ispod haube", key="debug_mode")

    if "openai_api_key" not in st.session_state:
        st.session_state["openai_api_key"] = get_openai_key()

    with st.sidebar:
        if st.button('Odjava'):
            authenticator.logout()
        container = st.sidebar.container(border=True)
        container.write("Postavke")
    
    render_chatbot()

    # Reset conversation
    if(st.button("Resetiraj razgovor")):
        st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam!"}]
        st.rerun()

    

else:
    st.write("Bok👋🏻 Kako bi mogao koristiti EduBot, moraš se prijaviti.")
    
    authenticator.login(justify_content="start")
