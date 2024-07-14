import streamlit as st

from llama_index.core.tools import ToolMetadata
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector
from llama_index.llms.openai import OpenAI
from llama_index.llms.ollama import Ollama
from llama_index.llms.anthropic import Anthropic

from llama_index.core.query_engine import CustomQueryEngine
from llama_index.core.tools import QueryEngineTool
from llama_index.core.selectors import LLMSingleSelector
from llama_index.core.query_engine import RouterQueryEngine


from modules.raptor_module import RAPTOR

from settings import get_llm

class LlmQueryEngine(CustomQueryEngine):
    """Custom query engine for direct calls to the LLM model."""

    llm_openai: OpenAI | None
    llm_ollama: Ollama | None
    llm_anthropic: Anthropic | None
    prompt: str

    def custom_query(self, query_str: str):
        if self.llm_openai is not None:
            llm = self.llm_openai
        elif self.llm_ollama is not None:
            llm = self.llm_ollama
        elif self.llm_anthropic is not None:
            llm = self.llm_anthropic
        else:
            raise ValueError("No LLM available for querying.")

        llm_prompt = self.prompt.format(query=query_str)
        
        llm_response = llm.complete(llm_prompt)
        
        return str(llm_response)

def intent_recognition(user_prompt: str, velociraptor: RAPTOR, sql_engine, web_scraper_engine):
    
    assert user_prompt is not None
    assert velociraptor is not None
    assert sql_engine is not None
    assert web_scraper_engine is not None

    # generic query engine - direct to LLM
    llm_settings = get_llm()

    # Determine the type of LLM and instantiate LlmQueryEngine accordingly
    if isinstance(llm_settings, OpenAI):
        llm_query_engine = LlmQueryEngine(llm_openai=llm_settings, prompt=st.session_state["intent_agent_settings"]["direct_llm_prompt"])
    elif isinstance(llm_settings, Ollama):
        llm_query_engine = LlmQueryEngine(llm_ollama=llm_settings, prompt=st.session_state["intent_agent_settings"]["direct_llm_prompt"])
    elif isinstance(llm_settings, Anthropic):
        llm_query_engine = LlmQueryEngine(llm_anthropic=llm_settings, prompt=st.session_state["intent_agent_settings"]["direct_llm_prompt"])
    else:
        raise ValueError("Unsupported LLM type")

    llm_tool = QueryEngineTool.from_defaults(
        query_engine=llm_query_engine,
        name="llm_query_tool",
        description= st.session_state["intent_agent_settings"]["llm_query_tool_description"],
    )
    
    raptor_query_engine = velociraptor.query_engine
    raptor_tool = QueryEngineTool.from_defaults(
    query_engine=raptor_query_engine,
    name="raptor_query_engine",
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
        selector=LLMSingleSelector.from_defaults(llm=get_llm()),
        query_engine_tools=[
            llm_tool,
            raptor_tool,
            sql_rag_tool,
            web_scraper_tool
        ],
    )
    
    query = "********************************************\n\n<query>\n" + user_prompt + "\n</query>"
    
    print("*\n" + query + "\n*")
    
    response = router_query_engine.query(query)
    
    ###### PRINT RAPTOR NODES
    raptor_nodes = velociraptor.retriever.retrieve(query)
    print("Retrieved Nodes from RaptorRetriever:")
    for node in raptor_nodes:
        print(node.text)
    ######
   
    print(f"""
          RESPONSE RouterQueryEngine
          *********************************************
          {response}
          *********************************************
          """) 
    
    intent = response.metadata["selector_result"].selections[0]
    
    # if the user context is included and intent is RAPTOR search
    
    if intent.index == 3:
        print("WEB SCRAPER INTENT")
        tailored_response = get_llm().complete(
            f"***Instructions for answering the user query:***\n"
            f"Always make sure to answer in Croatian language.\n"
            f"Your task is to present the user with the latest news from the website. Here are the news:\n"  
            f""""
                <NEWS START>
                {response}
                <NEWS END>
            """
        )
        return tailored_response, intent
    
    if intent.index == 2:
        print("SQL RAG INTENT")
        tailored_response = get_llm().complete(
            f"***Instructions for answering the user query:***\n"
            f"Always make sure to answer in Croatian language.\n"
            f"Based on user query and result SQL query result. Answer the user question directly to user.\n"
            f"User has asked the following question:\n"
            f"<LATEST USER QUERY>\n"
                f"{user_prompt} \n"
                f"<LATEST USER QUERY END>\n"
            f"Here is the result of the SQL query:\n"
            f""""
                <SQL QUERY RESULT START>
                {response}
                <SQL QUERY RESULT END>
            """
        )
        return tailored_response, intent
    
    if not st.session_state["use_full_conversation"]:
    
        if intent.index == 1 and st.session_state["user_context_included"] :
            print("RAPTOR INTENT | ONLY LAST USER QUERY | USER CONTEXT INCLUDED")
            tailored_response = get_llm().complete(
                f"***Instructions for answering the user query:***\n"
                f"Always make sure to answer in Croatian language, but do not translate the code snippets nor IT terms.\n"
                f"You are a good professor and know how to explain things well to students of different levels. Student is asking you the following question:\n"
                f"<LATEST USER QUERY>\n"
                f"{user_prompt} \n"
                f"<LATEST USER QUERY END>\n"
                f"Answer the student directly.\n"
                f"First determine if the question is IT-related and programming related.\n"
                f"<STUDENT CONTEXT START>\n"
                f"Student year of study: {stud_year_to_num(st.session_state['user_info']['study_year'])}. Note 1 are freshmen so explain to them in simple terms, and 5 are graduate students with high knowledge - use professional terms.\n"
                f"Student's programming knowledge: {st.session_state['user_info']['programming_knowledge']}. Note 1 is a beginner, 10 is an expert.\n"
                f"<STUDENT CONTEXT END>\n"
                f"Determine if the following <KNOWLEDGE> is IT-related or programming related. If it is, tailor the following <KNOWLEDGE> to the student's level based on <STUDENT CONTEXT> provided above and use code snippet in markdown if applicable.\n"
                f""""
                <KNOWLEDGE START>
                {response}
                <KNOWLEDGE END>
                """
                f"Final note, if the knowledge is not IT-related or programming related, provide a general explanation of the <KNOWLEDGE> without taking into account <STUDENT CONTEXT> nor use code snippets.\n"

            )
            return tailored_response, intent
        
        elif intent.index == 1:
            print("RAPTOR INTENT | ONLY LAST USER QUERY | NO USER CONTEXT")
            tailored_response = get_llm().complete(
                f"***Instructions for answering the user query:***\n"
                f"Always make sure to answer in Croatian language, but do not translate the code snippets nor IT terms.\n"
                f"You are a good professor and know how to explain things well to students of different levels. Student is asking you the following question:\n"
                f"<LATEST USER QUERY>\n"
                f"{user_prompt} \n"
                f"<LATEST USER QUERY END>\n"
                f"Answer the student directly.\n"
                f"Use the following knowledge to answer the question:\n"
                f"""
                <KNOWLEDGE START>
                {response}
                <KNOWLEDGE END>
                """
            )
            return tailored_response, intent
           
    else:
        if intent.index == 1 and st.session_state["user_context_included"] :
            print("RAPTOR INTENT | FULL CONVERSATION | USER CONTEXT INCLUDED")
            tailored_response = get_llm().complete(
                f"***Instructions for answering the user query:***\n"
                f"Always make sure to answer in Croatian language, but do not translate the code snippets nor IT terms.\n"
                f"You are a good professor and know how to explain things well to students of different levels. For context, here is full conversation with you so far:\n"
                f"{user_prompt}"
                f"\n Take the whole context and answer the student's latest question indicated under **LATEST USER QUERY**.\n"
                f"First determine if the question is IT-related and programming related.\n"
                f"<STUDENT CONTEXT START>\n"
                f"Student year of study: {stud_year_to_num(st.session_state['user_info']['study_year'])}. Note 1 are freshmen so explain to them in simple terms, and 5 are graduate students with high knowledge - use professional terms.\n"
                f"Student's programming knowledge: {st.session_state['user_info']['programming_knowledge']}. Note 1 is a beginner, 10 is an expert.\n"
                f"<STUDENT CONTEXT END>\n"
                f"Determine if the following <KNOWLEDGE> is IT-related or programming related. If it is, tailor the following <KNOWLEDGE> to the student's level based on <STUDENT CONTEXT> provided above and use code snippet in markdown if applicable.\n"
                f""""
                <KNOWLEDGE START>
                {response}
                <KNOWLEDGE END>
                """
                f"Final note, if the knowledge is not IT-related or programming related, provide a general explanation of the <KNOWLEDGE> without taking into account <STUDENT CONTEXT> nor use code snippets.\n"

            )
            return tailored_response, intent
        
        elif intent.index == 1:
            print("RAPTOR INTENT | FULL CONVERSATION | NO USER CONTEXT")
            tailored_response = get_llm().complete(
                f"***Instructions for answering the user query:***\n"
                f"Always make sure to answer in Croatian language, but do not translate the code snippets nor IT terms.\n"
                f"You are a good professor and know how to explain things well to students of different levels. For context, here is full conversation with you so far:\n"
                f"{user_prompt}"
                f"\n Take the whole context and answer the student's latest question indicated under **LATEST USER QUERY**.\n"
                f"<LATEST USER QUERY END>\n"
                f"Answer the student directly.\n"
                f"Use the following knowledge to answer the question:\n"
                f"""
                <KNOWLEDGE START>
                {response}
                <KNOWLEDGE END>
                """
            )
            return tailored_response, intent
        
        
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
