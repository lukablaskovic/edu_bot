import streamlit as st
from dotenv import load_dotenv
import os

def get_openai_key():
    if 'use_openai_env' not in st.session_state:
        st.session_state.use_openai_env = True
    
    if 'openai_api_key' not in st.session_state:
        st.session_state.openai_api_key = ""
        
    if st.session_state.use_openai_env:
        load_dotenv()
        openai_api_key = os.getenv('OPENAI_API_KEY')
        if not openai_api_key:
            st.error("Greška: OpenAI API ključ nije postavljen u okruženju.")
            st.write("> Molim te postavi svoj OpenAI API ključ u .env datoteku ili unesi ključ ručno.")
            st.stop()
        else:
            st.session_state.openai_api_key = openai_api_key
    else:
        openai_api_key = st.text_input("OpenAI API ključ", type="password", value=st.session_state.openai_api_key)
        if not openai_api_key:
            st.write("> Ipak, prije nego nastaviš, molim unesi svoj OpenAI API ključ. Ako ga nemaš, možeš ga dobiti na [OpenAI](https://platform.openai.com/signup).")
            st.error("Greška: Nemam OpenAI API ključ.")
            st.stop()
        else:
            st.session_state.openai_api_key = openai_api_key
    
    os.environ['OPENAI_API_KEY'] = st.session_state.openai_api_key
    return st.session_state.openai_api_key
