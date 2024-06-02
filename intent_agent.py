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


direct_llm_prompt = (
    "Given the user query, respond as best as possible following this guidelines:\n"
    "- If the intent of the user is to get information about the abilities of the AI, respond with: "
    "EduBot ti može pomoći u učenju, razumijevanju gradiva iz programiranja, provjeri bodova i obaveza na kolegiju, provjeri stanja vašeg projekta na Githubu. \n"
    "- If the intent of the user is harmful. Respond with: Nažalost, ne mogu ti pomoći s ovime. \n"
    "- If the intent of the user is just to chat respond back politely in Croatian and do not start conversations with him non-related to the faculty, programming and IT.\n"
    "- If the intent of the user is to get information outside of the context given, respond with: "
    "E to ne znam! Molim te pitaj me nešto u kontekstu fakulteta Informatike i gradiva iz programiranja...\n"
    "Query: {query}"
)

class LlmQueryEngine(CustomQueryEngine):
    """Custom query engine for direct calls to the LLM model."""

    llm: OpenAI
    prompt: str

    def custom_query(self, query_str: str):
        llm_prompt = self.prompt.format(query=query_str)
        llm_response = self.llm.complete(llm_prompt)
        return str(llm_response)

def intent_recognition(prompt: str, velociraptor: RAPTOR):
    
    assert prompt is not None
    assert velociraptor is not None
    
    # generic query engine - direct to LLM
    llm_query_engine = LlmQueryEngine(llm=OpenAI(model="gpt-3.5-turbo"), prompt=direct_llm_prompt)
    llm_tool = QueryEngineTool.from_defaults(
        query_engine=llm_query_engine,
        name="llm_query_tool",
        description=(
            "Useful for when the INTENT of the user isnt clear, is broad, "
            "or when the user is asking general questions that have nothing "
            "to do with the faculty or programming. Use this tool when the other tool is not useful."
        ),
    )
    
    raptor_query_engine = velociraptor.query_engine
    raptor_tool = QueryEngineTool.from_defaults(
    query_engine=raptor_query_engine,
    name="vector_query_tool",
    description=(
        "Useful for retrieving specific context about the faculty, programming,"
        "javascript, python, classes at the Faculty of Informatics, scripts and pdf files,"
        "courses details, and help with programming assignments and exercises."),
    )
    
    router_query_engine = RouterQueryEngine(
        selector=LLMSingleSelector.from_defaults(),
        query_engine_tools=[
            llm_tool,
            raptor_tool,
        ],
    )
    
    response = router_query_engine.query(prompt)
    print("response.metadata['selector_result']", response.metadata["selector_result"])
    intent = response.metadata["selector_result"].selections[0]
    return response, intent

def get_intent_description(intent: ToolMetadata) -> str:
    intents = {
        0: "llm_tool",
        1: "raptor_tool"
    }
    
    intent_index = intent.index 
    return intents.get(intent_index, "Unknown intent")
