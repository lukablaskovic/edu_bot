import os

import streamlit as st
from streamlit_google_auth import Authenticate

from openai_key import get_openai_key
from chatbot import render_chatbot
from modules.sqlrag_module import get_tables 
from settings import initialize_settings, save_prompt

# import logging
# logging.basicConfig(level=logging.DEBUG)

st.set_page_config(
    page_title="EduBot",
    page_icon="🤖",
)

st.title('🤖🎓EduBot')

st.sidebar.title('🤖🎓EduBot')
st.sidebar.markdown("**Chatbot za personalizaciju nastavnih materijala**")

st.sidebar.markdown(
    "EduBot🤖🎓 je chatbot za studente i nastavnike Fakulteta informatike u Puli. Koristi velike jezične modele (LLM) za prepoznavanje namjera korisnika i generiranje odgovora.\n\n"
    "EduBot može odgovarati na pitanja iz dokumenata pohranjenih u bazi znanja (📚Datoteke). Korisnik može dodavati, brisati i definirati koje datoteke će se koristiti za obogaćivanje znanja EduBota.\n\n"
    "Korisnik može pohraniti informacije o sebi u 👤Korisničkom profilu kako bi EduBot prilagodio odgovore, npr. prema znanju iz programiranja.\n\n"
    "EduBot također može dohvaćati podatke iz baze podataka koristeći SQL-RAG tehniku."
)

st.sidebar.write("Autor: [Luka Blašković](https://github.com/lukablaskovic)")

st.sidebar.write("Source kôd dostupan [ovdje](https://github.com/lukablaskovic/edu_bot).")


st.write("Session State: ")
st.write("top k :", st.session_state["intent_agent_settings"]["similarity_top_k"])
st.write("tables used:", st.session_state["sql_rag_tables"])
st.write("max num posts:", st.session_state["web_scraper_settings"]["max_number_of_posts"])
st.write("selected_gpt:", st.session_state["llm_selection"]["selected_gpt"])


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

def raptor_settings():
    st.radio(
        "RAPTOR Retriever Mode",
        options=["collapsed", "tree_traversal",],
        help="Odaberi način pretraživanja klastera u RAPTOR-u. 'collapsed' pristup postavlja sve čvorove na istu razinu i evaluira sličnost čvorov simultano. 'tree_traversal' pristup koristi stablo za pretraživanje klastera i evaluira sličnost čvorova po razini stabla.",
        on_change=lambda: st.session_state["intent_agent_settings"].update(
            {"retriever_mode": st.session_state["temp_retriever_mode"]}
        ),
        key="temp_retriever_mode",
    )
    st.number_input("Unesi top-k", 
                    min_value=1, 
                    max_value=10,
                    help="Odaberi broj najrelevantnijih klastera koje će RAPTOR koristiti za pretraživanje.",  
                    key="temp_similarity_top_k",
                    value=st.session_state["intent_agent_settings"]["similarity_top_k"],
                    on_change=lambda: st.session_state["intent_agent_settings"].update(
                        {"similarity_top_k": st.session_state["temp_similarity_top_k"]} 
                    )
    )
    
    selected_embedding_model = st.radio(
                "Odaberi embedding model koji želiš koristiti",
                ('text-embedding-3-small', 'text-embedding-3-large'),
                help="Embedding model koji će se koristiti za embedding klastera prilikom izrade RAPTOR stabla i pozivanja RAPTOR Retriever-a.",
                
                on_change=lambda: st.session_state["llm_selection"].update(
                    {"selected_embedding_model": st.session_state["temp_selected_embedding_model"]}
                ),
                key="temp_selected_embedding_model",
            )

def sql_rag_settings():
    st.write("Označi tablice iz baze podataka koje će se koristiti za SQL-RAG")
    
    # Tables which will be used for SQL-RAG        
    tables = get_tables()
    selected_tables = {}
    
    for table in tables:
        selected_tables[table] = st.checkbox(table, 
                                                key=f"sql_rag_table_{table}", 
                                                on_change= lambda: st.session_state["sql_rag_tables"].update(
                                                    {table: st.session_state[f"sql_rag_table_{table}"]}),
                                                value=st.session_state["sql_rag_tables"][table]
                                                )



def web_scraper_settings():
    st.write("Web Scraper Settings (To-Do)")
    
    
    slider_value = st.slider(
        "Odaberi maksimalni broj najnovijih objava koje želiš da proučim sa stranica Sveučilišta/Fakulteta",
        min_value=1, 
        max_value=100,
        value=st.session_state["web_scraper_settings"]["max_number_of_posts"],
        key="temp_web_scraper_max_number_of_posts",
        on_change= lambda: st.session_state["web_scraper_settings"].update(
            {"max_number_of_posts": st.session_state["temp_web_scraper_max_number_of_posts"]}
        )
    )

def intent_recognition_settings():
    st.checkbox("Koristi cijeli razgovor kao kontekst", key="use_full_conversation")
    st.text_area(
        label="Direct LLM Prompt",
        value=st.session_state["intent_agent_settings"]["direct_llm_prompt"],
        on_change=lambda: st.session_state["intent_agent_settings"].update(
            {"direct_llm_prompt": st.session_state["temp_direct_llm_prompt"]}
        ),
        key="temp_direct_llm_prompt", 
        height=200
    )
    st.button(label="Spremi", key="btn_save_direct_llm_settings", type="primary", on_click=lambda: save_prompt("./prompts/DIRECT_LLM_PROMPT.txt", st.session_state["temp_direct_llm_prompt"]))

    st.text_area(
        label="Query Engine Description",
        value=st.session_state["intent_agent_settings"]["llm_query_tool_description"],
        on_change=lambda: st.session_state["intent_agent_settings"].update(
            {"llm_query_tool_description": st.session_state["temp_llm_query_tool_description"]}
        ),
        key="temp_llm_query_tool_description", 
        height=200
    )
    st.button(label="Spremi", key="btn_save_query_engine_desc", type="primary", on_click=lambda: save_prompt("./prompts/LLM_QUERY_TOOL_DESCRIPTION.txt", st.session_state["temp_llm_query_tool_description"]))

    st.divider()
    
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
            key="temp_raptor_query_tool_description",
            height=200
        )
    st.button(label="Spremi", key="btn_save_raptor_settings", type="primary", on_click=lambda: save_prompt("./prompts/RAPTOR_QUERY_TOOL_DESCRIPTION.txt", st.session_state["temp_raptor_query_tool_description"]))
    st.divider()
    
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
            key="temp_sql_rag_query_tool_description",
            height=200
        )
        
    st.button(label="Spremi", key="btn_save_sqlrag_settings", type="primary", on_click=lambda: save_prompt("./prompts/SQL_RAG_QUERY_TOOL_DESCRIPTION.txt", st.session_state["temp_sql_rag_query_tool_description"]))

if st.session_state['connected']:
    
    col1, col2 = st.columns([3, 1])

    with col1:
        st.write(f"Hej, {st.session_state['user_info'].get('name')}👋🏻")
        st.write("Uspješna prijava! Huuray! 🎉")
        st.write("""Tu sam da ti olakšam tvoju studentsku avanturu na [Fakultetu informatike](https://fipu.unipu.hr/). Mogu ti pomoći s pitanjima o studiju, predmetima, profesorima, projektima i još mnogo toga!""")
        st.write("Nije ti jasan silabus nekog kolegija, teorija iz skripte, problem iz programiranja ili te pak zanima koliko ti nedostaje bodova za prolaz iz nekog kolegija?")

    with col2:
        debug_mode_on = st.toggle("Ispod haube", key="debug_mode")

    with st.sidebar:
        if st.button('Odjava'):
            authenticator.logout()
        container = st.sidebar.container(border=True)
        
        with st.expander("Postavke | Odabir modela", expanded=False):
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
                st.write("Mistral Settings (To-Do)")
            else:
                st.write("Gemma Settings (To-Do)")
                
        with st.expander("Postavke | Intent Recognition", expanded=False):
            intent_recognition_settings()

        with st.expander("Postavke | RAPTOR", expanded=False):
            raptor_settings()
            
        with st.expander("Postavke | SQL-RAG", expanded=False):
            sql_rag_settings()
        
        with st.expander("Postavke | Web Scraper", expanded=False):
            web_scraper_settings()
            
    render_chatbot()

    # Reset conversation.
    if(st.button("Resetiraj razgovor")):
        st.session_state["messages"] = [{"role": "assistant", "content": "Tu sam! Kako ti mogu pomoći?🤖"}]
        st.rerun()

else:
    st.write("Bok👋🏻 Kako bi mogao koristiti EduBot, moraš se prijaviti.")
    
    authenticator.login(justify_content="start")
