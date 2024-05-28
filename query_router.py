from llama_index.core.tools import ToolMetadata
from llama_index.core.selectors import LLMSingleSelector, LLMMultiSelector

choices = [
        ToolMetadata(description="Able to read unstructured data such as documents and images", name="raptor"),
        ToolMetadata(description="Used for querying over structured data", name="sql_rag"),
        ToolMetadata(description="Connects to Github repo and provides details about repository", name="github_rag")
    ]

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

