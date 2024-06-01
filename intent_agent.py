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

from modules.raptor_module import RAPTOR


choices = [
        ToolMetadata(description="Use this when student asks some programming questions or other professional IT-related questoin", name="summarizer"),
        ToolMetadata(description="Called when user wants to read from database, such as his points", name="sql_rag"),
        ToolMetadata(description="Connects to Github repo and provides details about repository", name="github_rag"),
        #ToolMetadata(description="Random talk not related to programming", name="chitchat"),
    ]

direct_llm_prompt = (
    "Given the user query, respond as best as possible following this guidelines:\n"
    "- If the intent of the user is to get information about the abilities of the AI, respond with: "
    "EduBot ti može pomoći u učenju, razumijevanju gradiva iz programiranja, provjeri bodova i obaveza na kolegiju, provjeri stanja vašeg projekta na Githubu. \n"
    "- If the intent of the user is harmful. Respond with: Nažalost, ne mogu ti pomoći s ovime. \n"
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

# new intent recognition function
def intent_recognition(prompt: str, velociraptor: RAPTOR):
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

# to remove
def select_tool(query: str):
    
    selector = LLMMultiSelector.from_defaults()

    selector_result = selector.select(choices, query=query)
    
    print(selector_result)

    return selector_result.selections

def get_tool_metadata_by_index(index):
    return choices[index]

if __name__ == "__main__":
    query = "Kakvo je stanje projekta studenta zadnjih 6 mjeseci"
    selected_tool = select_tool(query)
    print(selected_tool)
