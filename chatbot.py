import streamlit as st
import openai
import os
from query_router import select_tool, get_tool_metadata_by_index
from dotenv import load_dotenv
from llama_index.core.tools import ToolMetadata

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.packs.raptor import RaptorPack
from llama_index.packs.raptor import RaptorRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.vector_stores.chroma import ChromaVectorStore
import chromadb
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

client = chromadb.PersistentClient()
collection = client.get_or_create_collection("pjs")

vector_store = ChromaVectorStore(chroma_collection=collection)


load_dotenv()

openn_ai_client = openai.Client()

def render_chatbot():
    
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam!"}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    if prompt := st.chat_input("Postavi mi pitanje ovdje..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.chat_message("user").write(prompt)
        
        # Reset conversation
        if(st.button("Resetiraj razgovor")):
            st.session_state["messages"] = [{"role": "assistant", "content": "Hej, tu sam!"}]
            st.rerun()
        try:
            with st.spinner("Odabirem alat..." if st.session_state.debug_mode else "..."):
                selected_tools = select_tool(prompt)

                tool_dict = {tool.index: get_tool_metadata_by_index(tool.index).name for tool in selected_tools}

                if selected_tools and st.session_state.debug_mode:
                    tools_list = "\n".join([f"{i+1}. {tool_dict[tool.index]}" for i, tool in enumerate(selected_tools)])
                    st.success(f"Odabrao sam sljedeće alate:\n{tools_list}")

                if 'summarizer' in tool_dict.values():

                    """
                    documents = SimpleDirectoryReader(input_files=["./uploaded_files/PJS1 - JavaScript osnove.pdf"]).load_data()
                    
                    raptor_pack = RaptorPack(
                        documents,
                        embed_model=OpenAIEmbedding(
                            model="text-embedding-3-small"
                        ),  # used for embedding clusters
                        llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"]), 
                        vector_store=vector_store,
                        similarity_top_k=2,
                        mode="collapsed", 
                        
                    )
                    """

                    retriever = RaptorRetriever(
                        [],
                        embed_model=OpenAIEmbedding(
                            model="text-embedding-3-small"
                        ),  # used for embedding clusters
                        llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"]), 
                        vector_store=vector_store, 
                        similarity_top_k=2,  
                        mode="collapsed", 
                    )
        
                    query_engine = RetrieverQueryEngine.from_args(
                        retriever, llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"])
                    )
                    response = query_engine.query(prompt)
                    
                    if (response):
                        st.session_state.messages.append({"role": "assistant", "content": str(response)})
                        st.chat_message("assistant").write(str(response))
                    
                
        except Exception as e:
            st.error(f"Error: {e}")
            return

SYSTEM_CONTENT = "You are a helpful assistant for students at the Faculty of Informatics. Respond to user queries and provide information about tools and resources available to students in Croatian language."

def get_chatbot_response(user_prompt, raptor_content):
    openai.api_key = st.session_state["openai_api_key"]
    response = openn_ai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_CONTENT},
            {"role": "assistant", "content": raptor_content}, 
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=500,
    )
    return response.choices[0].message.content
