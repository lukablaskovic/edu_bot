from llama_index.packs.raptor import RaptorPack
from llama_index.packs.raptor import RaptorRetriever
from llama_index.vector_stores.chroma import ChromaVectorStore
from dotenv import load_dotenv
from llama_index.core.tools import ToolMetadata
from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI
import streamlit as st
import chromadb
import logging

load_dotenv()


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

#client = chromadb.PersistentClient()
#collection = client.get_or_create_collection("pjs")

#vector_store = ChromaVectorStore(chroma_collection=collection)

#documents = SimpleDirectoryReader(input_files=["./uploaded_files/PJS1 - JavaScript osnove.pdf"]).load_data()

"""
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

class RAPTOR:
    def __init__(self, file_path, collection_name="pjs"):
        self.file_path = file_path
        self.collection_name = collection_name

        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO)
        self.logger.info("Initializing RAPTOR with file_path: %s and collection_name: %s", file_path, collection_name)

        try:
            self.client = chromadb.PersistentClient()
            self.collection = self.client.get_or_create_collection(collection_name)
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

            self.logger.info("Loading documents from file_path: %s", file_path)
            self.documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
            self.retriever = self.setup_retriever()
            self.query_engine = self.setup_query_engine()
        except Exception as e:
            self.logger.error("An error occurred during initialization: %s", e)
            raise

    def get_raptor_pack(self):
        try:
            self.logger.info("Creating RaptorPack")
            return RaptorPack(
                self.documents,
                embed_model=OpenAIEmbedding(model="text-embedding-3-small"),  # used for embedding clusters
                llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"]), 
                vector_store=self.vector_store,
                similarity_top_k=2,
                mode="collapsed", 
            )
        except Exception as e:
            self.logger.error("An error occurred while creating RaptorPack: %s", e)
            raise

    def setup_retriever(self):
        try:
            self.logger.info("Setting up RaptorRetriever")
            return RaptorRetriever(
                [],
                embed_model=OpenAIEmbedding(model="text-embedding-3-small"),  # used for embedding clusters
                llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"]), 
                vector_store=self.vector_store,
                similarity_top_k=2,
                mode="collapsed", 
            )
        except Exception as e:
            self.logger.error("An error occurred while setting up RaptorRetriever: %s", e)
            raise

    def setup_query_engine(self):
        try:
            self.logger.info("Setting up RetrieverQueryEngine")
            return RetrieverQueryEngine.from_args(
                self.retriever, llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"])
            )
        except Exception as e:
            self.logger.error("An error occurred while setting up RetrieverQueryEngine: %s", e)
            raise

    def get_response(self, prompt: str):
        try:
            self.logger.info("Querying with prompt: %s", prompt)
            query_engine = self.query_engine
            assert type(query_engine) == RetrieverQueryEngine
            response = query_engine.query(prompt)
            self.logger.info("Received response: %s", response)
            return response
        except Exception as e:
            self.logger.error("An error occurred while getting response: %s", e)
            raise
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
"""

"""
query_engine = RetrieverQueryEngine.from_args(
                    retriever, llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1, api_key=st.session_state["openai_api_key"])
                )
"""

#response = query_engine.query(prompt)
