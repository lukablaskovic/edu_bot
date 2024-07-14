import streamlit as st
from modules.sqlrag_module import get_tables
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.anthropic import Anthropic

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
DEFAULT_WEB_SCRAPER_QUERY_TOOL_DESCRIPTION = read_prompt_file("./prompts/default/DEFAULT_WEB_SCRAPER_QUERY_TOOL_DESCRIPTION.txt")

DEFAULT_SELECTED_MODEL = "GPT"
DEFAULT_SELECTED_GPT = "gpt-4o"
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
    
    if "intent_agent_settings" not in st.session_state:
        st.session_state["intent_agent_settings"] = {}
        st.session_state["intent_agent_settings"]["direct_llm_prompt"] = DEFUALT_DIRECT_LLM_PROMPT
        st.session_state["intent_agent_settings"]["llm_query_tool_description"] = DEFAULT_LLM_QUERY_TOOL_DESCRIPTION
        st.session_state["intent_agent_settings"]["raptor_query_tool_description"] = DEFAULT_RAPTOR_QUERY_TOOL_DESCRIPTION
        st.session_state["intent_agent_settings"]["sql_rag_query_tool_description"] = DEFUALT_SQL_RAG_QUERY_TOOL_DESCRIPTION
        st.session_state["intent_agent_settings"]["web_scraper_query_tool_description"] = DEFAULT_WEB_SCRAPER_QUERY_TOOL_DESCRIPTION
        
        st.session_state["intent_agent_settings"]["use_raptor"] = True
        st.session_state["intent_agent_settings"]["use_sql_rag"] = True
        st.session_state["intent_agent_settings"]["use_web_scraper"] = True 
    
        # RAPTOR
        st.session_state["intent_agent_settings"]["similarity_top_k"] = 6
        st.session_state["intent_agent_settings"]["retriever_mode"] = "collapsed"
    
     # sql-rag
    if "sql_rag_tables" not in st.session_state:
        st.session_state["sql_rag_tables"] = {}
        
        tables = get_tables()
        for table in tables:
            st.session_state["sql_rag_tables"][table] = True
    
    st.session_state["generated_query.text"] = None
    
    # web scraping tool
    if "web_scraper_settings" not in st.session_state:
        st.session_state["web_scraper_settings"] = {}
        st.session_state["web_scraper_settings"]["max_number_of_posts"] = 15
        st.session_state["web_scraper_settings"]["selected_web_url"] = "https://www.unipu.hr/novosti"
    
    if "user_context_included" not in st.session_state:
        st.session_state["user_context_included"] = False
    
def get_llm():
    """
    Get LLM settings.
    """
    if "llm_selection" not in st.session_state:
        initialize_settings()
        print("***Initialized settings!***")
    
    if st.session_state["llm_selection"]["selected_model"] == "GPT":
        return OpenAI(model=st.session_state["llm_selection"]["selected_gpt"], temperature=0.1, api_key=st.session_state["openai_api_key"])
    
    # https://ollama.com/library/mistral:7b
    elif st.session_state["llm_selection"]["selected_model"] == "mistral:7b":
        try:
            return Ollama(model="mistral", temperature=0.1)
        except ValueError as e:
            print(f"Model 'mistral' is not recognized: {e}")
            raise ValueError("Invalid model 'mistral' for Ollama.")
        
    # https://ollama.com/library/gemma
    elif st.session_state["llm_selection"]["selected_model"] == "gemma:7b":
        try:
            return Ollama(model="gemma:7b", temperature=0.1)
        except ValueError as e:
            print(f"Model 'gemma:7b' is not recognized: {e}")
            raise ValueError("Invalid model 'gemma:7b' for Ollama.")
        
    # https://ollama.com/library/llama3
    elif st.session_state["llm_selection"]["selected_model"] == "llama3:8b":
        try:
            return Ollama(model="llama3", temperature=0.1)
        except ValueError as e:
            print(f"Model 'llama3' is not recognized: {e}")
            raise ValueError("Invalid model 'llama3' for Ollama.")
        
    # https://docs.llamaindex.ai/en/latest/examples/llm/anthropic/
    elif st.session_state["llm_selection"]["selected_model"] == "Claude 3 Opus":
        try:
            return Anthropic(model="claude-3-opus-20240229", temperature=0.1)
        except ValueError as e:
            print(f"Model 'claude-3-opus-20240229' is not recognized: {e}")
            raise ValueError("Invalid model 'claude-3-opus-20240229' for Anthropic.")
        
    # https://docs.llamaindex.ai/en/latest/examples/llm/anthropic/
    elif st.session_state["llm_selection"]["selected_model"] == "Claude 3 Sonnet":
        try:
            return Anthropic(model="claude-3-sonnet-20240229", temperature=0.1)
        except ValueError as e:
            print(f"Model 'claude-3-sonnet-20240229' is not recognized: {e}")
            raise ValueError("Invalid model 'claude-3-sonnet-20240229' for Anthropic.")
        
    # https://docs.llamaindex.ai/en/latest/examples/llm/anthropic/
    elif st.session_state["llm_selection"]["selected_model"] == "Claude 3 Haiku":
        try:
            return Anthropic(model="claude-3-haiku-20240307", temperature=0.1)
        except ValueError as e:
            print(f"Model 'claude-3-haiku-20240307' is not recognized: {e}")
            raise ValueError("Invalid model 'claude-3-haiku-20240307' for Anthropic.")
    