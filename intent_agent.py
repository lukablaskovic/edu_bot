from llama_index.core.tools import ToolMetadata
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.core import VectorStoreIndex
from llama_index.llms.openai import OpenAI
from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.response_synthesizers import ResponseMode
from llama_index.core import VectorStoreIndex
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.query_engine import RouterQueryEngine
from typing import Dict
from modules.raptor_module import RAPTOR
import streamlit as st

from llama_index.core.query_engine import RetrieverQueryEngine

class LlmQueryEngine(CustomQueryEngine):
    """Custom query engine for direct calls to the LLM model."""

    llm: OpenAI
    prompt: str

    def custom_query(self, query_str: str):
        llm_prompt = self.prompt.format(query=query_str)
        llm_response = self.llm.complete(llm_prompt)
        return str(llm_response)

def intent_recognition(prompt: str, velociraptor: RAPTOR, sql_engine: RetrieverQueryEngine):
    
    assert prompt is not None
    assert velociraptor is not None
    
    # generic query engine - direct to LLM
    llm_query_engine = LlmQueryEngine(llm=OpenAI(model="gpt-3.5-turbo"), prompt=st.session_state["intent_agent_settings"]["direct_llm_prompt"])
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
    
    print("sqlengine:", sql_engine)
    
    router_query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[
            llm_tool,
            raptor_tool,
            sql_rag_tool
        ],
    )
    
    response = router_query_engine.query(prompt)
    print("response.metadata['selector_result']", response.metadata["selector_result"])
    intent = response.metadata["selector_result"].selections[0]
    
    #if intent.index == 2:
        # must return sql select query which was generated
    
    return response, intent

def get_intent_description(intent: ToolMetadata) -> str:
    intents = {
        0: "llm_tool",
        1: "raptor_tool",
        2: "sql_rag_tool"
    }
    
    intent_index = intent.index 
    return intents.get(intent_index, "Unknown intent")
