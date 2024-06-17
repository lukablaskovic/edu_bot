import streamlit as st

from llama_index.core.tools import ToolMetadata
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.query_engine import RouterQueryEngine

from modules.raptor_module import RAPTOR

from settings import get_llm_settings

class LlmQueryEngine(CustomQueryEngine):
    """Custom query engine for direct calls to the LLM model."""

    llm: OpenAI
    prompt: str

    def custom_query(self, query_str: str):
        llm_prompt = self.prompt.format(query=query_str)
        llm_response = self.llm.complete(llm_prompt)
        return str(llm_response)

LLM_settings = get_llm_settings()

def intent_recognition(prompt: str, velociraptor: RAPTOR, sql_engine, web_scraper_engine):
    
    assert prompt is not None
    assert velociraptor is not None
    assert sql_engine is not None
    assert web_scraper_engine is not None

    # generic query engine - direct to LLM
    llm_query_engine = LlmQueryEngine(llm=OpenAI(model=LLM_settings), prompt=st.session_state["intent_agent_settings"]["direct_llm_prompt"])
    llm_tool = QueryEngineTool.from_defaults(
        query_engine=llm_query_engine,
        name="llm_query_tool",
        description= st.session_state["intent_agent_settings"]["llm_query_tool_description"],
        
    )
    
    raptor_query_engine = velociraptor.query_engine
    raptor_tool = QueryEngineTool.from_defaults(
    query_engine=raptor_query_engine,
    name="vector_query_tool",
    description= st.session_state["intent_agent_settings"]["raptor_query_tool_description"],
    )
    
    sql_query_engine = sql_engine
    sql_rag_tool = QueryEngineTool.from_defaults(
        query_engine=sql_query_engine,
        name="sql_rag_tool",
        description=st.session_state["intent_agent_settings"]["sql_rag_query_tool_description"]
    )
    
    web_scraper_query_engine = web_scraper_engine
    web_scraper_tool = QueryEngineTool.from_defaults(
        query_engine=web_scraper_query_engine,
        name="web_scraper_tool",
        description=st.session_state["intent_agent_settings"]["web_scraper_query_tool_description"]
    )
    router_query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[
            llm_tool,
            raptor_tool,
            sql_rag_tool,
            web_scraper_tool
        ],
    )
    
    query = "<query>\n" + prompt + "\n</query>"
    
    print("*\n" + query + "\n*")
    
    response = router_query_engine.query(query)
        
    intent = response.metadata["selector_result"].selections[0]
    
    return response, intent

def get_intent_description(intent: ToolMetadata) -> str:
    intents = {
        0: "llm_tool",
        1: "raptor_tool",
        2: "sql_rag_tool",
        3: "web_scraper_tool"
    }
    
    intent_index = intent.index 
    return intents.get(intent_index, "Unknown intent")

def stud_year_to_num(stud_year: str) -> int:
    mapping = {
        "1. prijediplomski": 1,
        "2. prijediplomski": 2,
        "3. prijediplomski": 3,
        "1. diplomski": 4,
        "2. diplomski": 5
    }
    
    return mapping.get(stud_year, None)
