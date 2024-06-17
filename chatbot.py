import os
from dotenv import load_dotenv

import pandas as pd
import streamlit as st

from llama_index.llms.openai import OpenAI
from llama_index.core import PromptTemplate

from modules.sqlrag_module import SQLQueryEngine, get_create_table_statement, get_sql_template
from modules.raptor_module import get_raptor
from modules.web_scraper_module import WebScraperQueryEngine
from intent_agent import intent_recognition, get_intent_description
from settings import get_llm_settings

load_dotenv()

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
                st.error(f"Greška [RAPTOR]: {e}")
                return

            try:
                table_schemas = []
                for table, is_used in st.session_state.get("sql_rag_tables", {}).items():
                    if is_used:
                        table_schemas.append(get_create_table_statement(table))
                schemas_str = "\n".join(table_schemas)

                sql_prompt = get_sql_template(schemas_str)

                sql_query_engine = SQLQueryEngine(prompt=sql_prompt, llm=OpenAI(model=get_llm_settings()))
            except Exception as e:
                st.error(f"Greška [SQL-RAG]: {e}")
                return
            
            web_scraper_engine = WebScraperQueryEngine(llm=OpenAI(model=get_llm_settings()))

            if st.session_state["user_context_included"]:
                if st.session_state.debug_mode:
                    st.info("Uključujem podatke o studentu kao kontekst")
            
            if st.session_state["use_full_conversation"]:
                if st.session_state.debug_mode:
                    st.info("Koristim cijeli razgovor")
                conversation = ""
                for msg in st.session_state.messages:
                    conversation += f"{msg['role'].upper()}: {msg['content']}\n"
                conversation += f"LATEST USER PROMPT: {prompt}"

                response, intent = intent_recognition(conversation, velociraptor, sql_query_engine, web_scraper_engine)
            else:
                if st.session_state.debug_mode:
                    st.info("Koristim samo zadnji upit")

                response, intent = intent_recognition(prompt, velociraptor, sql_query_engine, web_scraper_engine)

            print("__________________________INTENT___________________________")
            print("response:", response)
            print("intent:", intent)

            selected_intent = get_intent_description(intent)
            if st.session_state.debug_mode:
                st.success(f"Odabrao sam: {selected_intent} ✅")
            
            if st.session_state.debug_mode and selected_intent == "web_scraper_tool":
                st.info(f"Čitam najnovijih {st.session_state['web_scraper_settings']['max_number_of_posts']} objava s weba🌐🎓")
            
            if st.session_state.debug_mode and st.session_state["generated_query.text"]:
                st.code(st.session_state["generated_query.text"], language="sql")      
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
