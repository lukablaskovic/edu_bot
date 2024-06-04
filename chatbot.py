import streamlit as st
import openai
import os
from intent_agent import intent_recognition, get_intent_description
from dotenv import load_dotenv
import pandas as pd
from modules.raptor_module import get_raptor
from modules.sqlrag_module import get_sql_engine

load_dotenv()

# Configure logging

openn_ai_client = openai.Client()

def render_chatbot():
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Tu sam! Kako ti mogu pomoći?🤖"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Postavi mi pitanje ovdje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)

        with st.spinner("Odabirem alat..." if st.session_state.debug_mode else "..."):
        
            try:
                # caching
                if 'raptor' in st.session_state:
                    velociraptor = st.session_state["raptor"]
                else:
                    velociraptor = get_raptor(files=get_files() , force_rebuild=False)
            except Exception as e:
                st.error(f"Greška: {e}")
                return
            
            sql_query_engine = get_sql_engine()
            
            response, intent = intent_recognition(prompt, velociraptor, sql_query_engine)
            
            print("__________________________INTENT___________________________")

            print("response:", response)
            print("intent:", intent)
            
            if st.session_state.debug_mode:
                st.success(f"Odabrao sam: {get_intent_description(intent)}")
            
            try:
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
                    st.chat_message("assistant").write(str(response))
            except Exception as e:
                st.error(f"Greška: {e}")
            return

# will be removed
SYSTEM_CONTENT = "You are a helpful assistant for students at the Faculty of Informatics. Respond to user queries and provide information about tools and resources available to students in Croatian language."

def get_chatbot_response(user_prompt, raptor_content):
    openai.api_key = st.session_state["openai_api_key"]
    response = openn_ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "assistant", "content": raptor_content}, 
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content

UPLOAD_DIR = "uploaded_files"
STATE_FILE = "file_state.csv"

def get_files():
    df = pd.read_csv(STATE_FILE)
    
    used_files_df = df[df['is_used'] == True]
    
    used_files = used_files_df['Naziv datoteke'].tolist()
    
    full_paths = [os.path.join(UPLOAD_DIR, file) for file in used_files]
    print("full_paths", full_paths)
    return full_paths
    