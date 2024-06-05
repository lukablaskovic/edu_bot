import streamlit as st

DEFUALT_LLM_PROMPT = (
    "Given the user query, respond as best as possible following this guidelines:\n"
    "- If the intent of the user is to get information about the abilities of the AI, respond with: "
    "'EduBot ti može pomoći u učenju, razumijevanju gradiva iz programiranja, provjeri bodova i obaveza na kolegiju, provjeri stanja vašeg projekta na Githubu.'\n"
    "- If the intent of the user is harmful. Respond with: 'Nažalost, ne mogu ti pomoći s ovime.' \n"
    "- If the intent of the user is just to chat respond back politely in Croatian and do not start conversations with him non-related to the faculty, programming and IT.\n"
    "- If the intent of the user is to get information outside of the context given, respond with: "
    "'E to ne znam! Molim te pitaj me nešto u kontekstu fakulteta Informatike i gradiva iz programiranja...'\n"
    "Query: {query}"
)

DEFAULT_LLM_QUERY_TOOL_DESCRIPTION = (
            "Useful for when the INTENT of the user isnt clear, is broad, "
            "or when the user is asking general questions that have nothing "
            "to do with the faculty or programming. Use this tool when the other tool is not useful."
        )

DEFAULT_RAPTOR_QUERY_TOOL_DESCRIPTION = (
        "Useful for retrieving specific context about the faculty, programming,"
        "javascript, python, classes at the Faculty of Informatics, scripts and pdf files,"
        "courses details, and help with programming assignments and exercises."
    )

DEFUALT_SQL_RAG_QUERY_TOOL_DESCRIPTION = (
    "Useful for retrieving specific data from database,"
    "you use this tool when you identify that the user is asking for data that is stored in the database,"
    "and can identify tables and select query that is relevant to the user query."
)

def initialize_settings():
    """
    Initialize settings.
    """
    
    if "intent_agent_settings" not in st.session_state:
            st.session_state["intent_agent_settings"] = {}
    st.session_state["intent_agent_settings"]["direct_llm_prompt"] = DEFUALT_LLM_PROMPT
    st.session_state["intent_agent_settings"]["llm_query_tool_description"] = DEFAULT_LLM_QUERY_TOOL_DESCRIPTION
    st.session_state["intent_agent_settings"]["use_raptor"] = True
    st.session_state["intent_agent_settings"]["use_sql_rag"] = True 
    st.session_state["intent_agent_settings"]["raptor_query_tool_description"] = DEFAULT_RAPTOR_QUERY_TOOL_DESCRIPTION
    st.session_state["intent_agent_settings"]["sql_rag_query_tool_description"] = DEFUALT_SQL_RAG_QUERY_TOOL_DESCRIPTION
    st.session_state["intent_agent_settings"]["top_k"] = 2