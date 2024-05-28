import streamlit as st
import os
from dotenv import load_dotenv

def get_openai_key():
    use_env_key = st.sidebar.checkbox("Učitaj OpenAI API ključ iz okruženja")
    
    if use_env_key:
        load_dotenv()
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
    return openai_api_key
