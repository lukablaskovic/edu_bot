import streamlit as st
import os

from streamlit_google_auth import Authenticate
from openai_key import get_openai_key
from chatbot import render_chatbot
from dotenv import load_dotenv

from settings import initialize_settings

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

st.sidebar.write("Source kôd dostupan [ovdje](https://github.com/lukablaskovic/edu_bot).")

"st.session_state", st.session_state

authenticator = Authenticate(
    secret_credentials_path='google_credentials.json',
    cookie_name='edubot_cookie',
    cookie_key=os.getenv('COOKIE_KEY'),
    cookie_expiry_days=30,
    redirect_uri='http://localhost:8501',
)

authenticator.check_authentification()

if st.session_state['connected']:
    initialize_settings()
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"Hej, {st.session_state['user_info'].get('name')}👋🏻")
        st.write("Uspješna prijava! Huuray! 🎉")
        st.write("""Tu sam da ti olakšam tvoju studentsku avanturu na [Fakultetu informatike](https://fipu.unipu.hr/). Mogu ti pomoći s pitanjima o studiju, predmetima, profesorima, projektima i još mnogo toga!""")
        st.write("Nije ti jasan silabus nekog kolegija, teorija iz skripte, problem iz programiranja ili te pak zanima koliko ti nedostaje bodova za prolaz i što moraš sve dovršiti za taj projekt iz Programskog🔥?")

    with col2:
        debug_mode_on = st.toggle("Ispod haube", key="debug_mode")

    def intent_recognition_settings():
        
        st.text_area(
            label="Direct LLM Prompt",
            value=st.session_state["intent_agent_settings"]["direct_llm_prompt"],
            on_change=lambda: st.session_state["intent_agent_settings"].update(
                {"direct_llm_prompt": st.session_state["temp_direct_llm_prompt"]}
            ),
            key="temp_direct_llm_prompt"
        )
        
        st.text_area(
            label="Query Engine Description",
            value=st.session_state["intent_agent_settings"]["llm_query_tool_description"],
            on_change=lambda: st.session_state["intent_agent_settings"].update(
                {"llm_query_tool_description": st.session_state["temp_llm_query_tool_description"]}
            ),
            key="temp_llm_query_tool_description"
        )
        
        use_raptor = st.checkbox("Koristi RAPTOR Engine", 
                                 value= st.session_state["intent_agent_settings"]["use_raptor"],
                                 on_change=lambda: st.session_state["intent_agent_settings"].update(
                                        {"use_raptor": st.session_state["temp_use_raptor"]}
                                    ), 
                                 key="temp_use_raptor")
        if use_raptor:
            st.text_area(
                label="RAPTOR Engine Description",
                value=st.session_state["intent_agent_settings"]["raptor_query_tool_description"],
                on_change=lambda: st.session_state["intent_agent_settings"].update(
                    {"raptor_query_tool_description": st.session_state["temp_raptor_query_tool_description"]}
                ),
                key="temp_raptor_query_tool_description"
            )
        
        use_sql_rag = st.checkbox("Koristi SQL-RAG Engine", 
                                 value= st.session_state["intent_agent_settings"]["use_sql_rag"],
                                 on_change=lambda: st.session_state["intent_agent_settings"].update(
                                        {"use_sql_rag": st.session_state["temp_use_sql_rag"]}
                                    ), 
                                 key="temp_use_sql_rag")
        if use_sql_rag:
            st.text_area(
                label="SQL-RAG Engine Description",
                value=st.session_state["intent_agent_settings"]["sql_rag_query_tool_description"],
                on_change=lambda: st.session_state["intent_agent_settings"].update(
                    {"sql_rag_query_tool_description": st.session_state["temp_sql_rag_query_tool_description"]}
                ),
                key="temp_sql_rag_query_tool_description"
            )
    
    def raptor_settings():
        st.radio(
            "RAPTOR Retriever Mode",
            options=["collapsed_retrieval", "tree_traversal_retrieval",],
            on_change=lambda: st.session_state["intent_agent_settings"].update(
                {"retriever_mode": st.session_state["temp_retriever_mode"]}
            ),
            key="temp_retriever_mode",
        )
        st.number_input("Unesi top-k", min_value=1, max_value=10, value=st.session_state["intent_agent_settings"]["top_k"], key="top_k")

    
    def sql_rag_settings():
        st.write("Ovdje možeš postaviti SQL-RAG.")
    
    with st.sidebar:
        if st.button('Odjava'):
            authenticator.logout()
        container = st.sidebar.container(border=True)
        
        with st.expander("Postavke | Odabir modela", expanded=False):
            st.write("Odabir modela")
            st.radio(
                "Odaberi LLM koji želiš koristiti za pogon EduBota🤖",
                options=["GPT", "Mistral", "Gemma"],
                on_change=lambda: st.session_state["llm_selection"].update(
                    {"selected_model": st.session_state["temp_selected_model"]}
                ),
                key="temp_selected_model",
            )
            if(st.session_state["llm_selection"]["selected_model"] == "GPT"):
                st.session_state["openai_api_key"] = get_openai_key()
                st.checkbox("Učitaj OpenAI API ključ iz okruženja", key="use_openai_env", help="Chekiraj ovu opciju ako želiš da se ključ učita iz okruženja. Potrebno je u `.env` datoteku dodati `OPENAI_API_KEY` ključ.")


                selected_gpt = st.radio(
                    "Odaberi GPT model koji želiš koristiti",
                    ('gpt-3.5-turbo', 'gpt-4'),
                    on_change=lambda: st.session_state["llm_selection"].update(
                        {"selected_gpt": st.session_state["temp_selected_gpt"]}
                    ),
                    key="temp_selected_gpt",
                )

                
            elif(st.session_state["llm_selection"]["selected_model"] == "Mistral"):
                st.write("Mistral Settings")
            else:
                st.write("Gemma Settings")
        with st.expander("Postavke | Intent Recognition", expanded=False):
            intent_recognition_settings()

        with st.expander("Postavke | RAPTOR", expanded=False):
            raptor_settings()
            
        with st.expander("Postavke | SQL-RAG", expanded=False):
            sql_rag_settings()
            
    render_chatbot()

    # Reset conversation.
    if(st.button("Resetiraj razgovor")):
        st.session_state["messages"] = [{"role": "assistant", "content": "Tu sam! Kako ti mogu pomoći?🤖"}]
        st.rerun()

else:
    st.write("Bok👋🏻 Kako bi mogao koristiti EduBot, moraš se prijaviti.")
    
    authenticator.login(justify_content="start")
