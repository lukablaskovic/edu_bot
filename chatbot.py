import streamlit as st
import openai
import os
from intent_agent import intent_recognition, get_intent_description
from dotenv import load_dotenv
import pandas as pd
from modules.raptor_module import get_raptor
from modules.sqlrag_module import SQLQueryEngine
from llama_index.llms.openai import OpenAI
from settings import get_llm_settings
from llama_index.core import PromptTemplate

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
                    velociraptor = get_raptor(files=get_files(), force_rebuild=False)
            except Exception as e:
                st.error(f"Greška: {e}")
                return

            qa_prompt = PromptTemplate(
                "Context information is below.\n"
                "---------------------\n"
                "You are a professional SQL developer. You are given a task to write a SQL query to retrieve data from the database.\n"
                "---------------------\n"
                "CREATE TABLE users (\n"
                "id INTEGER NOT NULL, \n"
                "first_name VARCHAR(16) NOT NULL, \n"
                "last_name VARCHAR(16) NOT NULL, \n"
                "email VARCHAR(32) NOT NULL, \n"
                "study_year VARCHAR(16) NOT NULL, \n"
                "about_me VARCHAR(256) NOT NULL, \n"
                "programming_knowledge INTEGER NOT NULL, \n"
                "PRIMARY KEY (id))\n"
                "\n"
                "CREATE TABLE PJS_points (\n"
                "id INTEGER NOT NULL UNIQUE,\n"
                "user_id INTEGER NOT NULL,\n"
                "exam_1_points INTEGER NOT NULL DEFAULT 0,\n"
                "exam_2_points INTEGER NOT NULL DEFAULT 0,\n"
                "exam_3_points INTEGER NOT NULL DEFAULT 0,\n"
                "exam_4_points INTEGER NOT NULL DEFAULT 0,\n"
                "exam_5_points INTEGER NOT NULL DEFAULT 0,\n"
                "exam_total_points INTEGER NOT NULL DEFAULT 0,\n"
                "PRIMARY KEY(id AUTOINCREMENT),\n"
                "FOREIGN KEY(user_id) REFERENCES users(id))\n"
                "---------------------\n"
                "Given the database schemas and example rows, structure the SQL query from given User prompt\n"
                "User prompt: {query_str}\n"
            )

            
            sql_query_engine = SQLQueryEngine(prompt=qa_prompt ,llm=OpenAI(model=get_llm_settings()))

            if st.session_state["use_full_conversation"]:
                if st.session_state.debug_mode:
                    st.info("Koristim cijeli razgovor")
                conversation = ""
                for msg in st.session_state.messages:
                    conversation += f"{msg['role'].upper()}: {msg['content']}\n"
                conversation += f"LATEST USER PROMPT: {prompt}"
                print("***************************************full_conversation:", conversation)
                response, intent = intent_recognition(conversation, velociraptor, sql_query_engine)
            else:
                if st.session_state.debug_mode:
                    st.info("Koristim samo zadnji upit")
                print("________________________________________prompt:", prompt)
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

UPLOAD_DIR = "uploaded_files"
STATE_FILE = "file_state.csv"

def get_files():
    df = pd.read_csv(STATE_FILE)
    used_files_df = df[df['is_used'] == True]
    used_files = used_files_df['Naziv datoteke'].tolist()
    full_paths = [os.path.join(UPLOAD_DIR, file) for file in used_files]
    print("full_paths", full_paths)
    return full_paths
