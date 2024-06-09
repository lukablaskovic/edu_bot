import streamlit as st
from modules.sqlrag_module import get_tables


def read_prompt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        st.error("Error reading the file. Please check the file encoding.")
        return ""

def save_prompt(file_path, content):
    print("saving prompt!")
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            print("opened file!")
            file.write(content)
        st.success(f"Prompt successfully saved to {file_path}")
    except Exception as e:
        st.error(f"Error saving the prompt: {e}")

DEFUALT_DIRECT_LLM_PROMPT = read_prompt_file("./prompts/default/DEFUALT_DIRECT_LLM_PROMPT.txt")
DEFAULT_LLM_QUERY_TOOL_DESCRIPTION = read_prompt_file("./prompts/default/DEFAULT_LLM_QUERY_TOOL_DESCRIPTION.txt")
DEFAULT_RAPTOR_QUERY_TOOL_DESCRIPTION = read_prompt_file("./prompts/default/DEFAULT_RAPTOR_QUERY_TOOL_DESCRIPTION.txt")
DEFUALT_SQL_RAG_QUERY_TOOL_DESCRIPTION = read_prompt_file("./prompts/default/DEFAULT_SQL_RAG_QUERY_TOOL_DESCRIPTION.txt")

DEFAULT_SELECTED_MODEL = "GPT"
DEFAULT_SELECTED_GPT = "gpt-3.5-turbo"
DEFAULT_SELECTED_EMBEDDING_MODEL = "text-embedding-3-small"

def initialize_settings():
    """
    Initialize settings.
    """
    
    if "llm_selection" not in st.session_state:
        st.session_state["llm_selection"] = {}
        st.session_state["llm_selection"]["selected_model"] = DEFAULT_SELECTED_MODEL
        st.session_state["llm_selection"]["selected_gpt"] = DEFAULT_SELECTED_GPT
        st.session_state["llm_selection"]["selected_embedding_model"] = DEFAULT_SELECTED_EMBEDDING_MODEL
    
    
    st.session_state["intent_agent_settings"] = {}
    st.session_state["intent_agent_settings"]["direct_llm_prompt"] = DEFUALT_DIRECT_LLM_PROMPT
    st.session_state["intent_agent_settings"]["llm_query_tool_description"] = DEFAULT_LLM_QUERY_TOOL_DESCRIPTION
    st.session_state["intent_agent_settings"]["use_raptor"] = True
    st.session_state["intent_agent_settings"]["use_sql_rag"] = True 
    st.session_state["intent_agent_settings"]["raptor_query_tool_description"] = DEFAULT_RAPTOR_QUERY_TOOL_DESCRIPTION
    st.session_state["intent_agent_settings"]["sql_rag_query_tool_description"] = DEFUALT_SQL_RAG_QUERY_TOOL_DESCRIPTION
    
    # RAPTOR
    st.session_state["intent_agent_settings"]["similarity_top_k"] = 5
    st.session_state["intent_agent_settings"]["retriever_mode"] = "collapsed"
    
     # sql-rag
    if "sql_rag_tables" not in st.session_state:
        st.session_state["sql_rag_tables"] = {}
        
        tables = get_tables()
        for table in tables:
            st.session_state["sql_rag_tables"][table] = True
    st.session_state["generated_query.text"] = None
    
def get_llm_settings():
    """
    Get LLM settings.
    """
    if "llm_selection" not in st.session_state:
        initialize_settings()
        print("***Initialized settings!***")
    
    if st.session_state["llm_selection"]["selected_model"] == "GPT":
        return st.session_state["llm_selection"]["selected_gpt"]