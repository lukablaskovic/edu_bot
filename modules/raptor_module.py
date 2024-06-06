from llama_index.packs.raptor import RaptorPack
from llama_index.packs.raptor import RaptorRetriever
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core.tools import ToolMetadata
from llama_index.embeddings.openai import OpenAIEmbedding

from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.llms.openai import OpenAI
import streamlit as st
import chromadb
import logging
import time
import os
import shutil
import gc
from dotenv import load_dotenv
load_dotenv()
from settings import get_llm_settings

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

logger.setLevel(logging.WARNING)


LLM_settings = get_llm_settings()

EMBEDDING_MODEL = st.session_state["llm_selection"]["selected_embedding_model"]
RETRIEVAL_METHOD = st.session_state["intent_agent_settings"]["retriever_mode"]
SIMILARITY_TOP_K = st.session_state["intent_agent_settings"]["similarity_top_k"]

class RAPTOR:
    def __init__(self, files, collection_name="pjs", force_rebuild=False):
        self.files = files
        self.collection_name = collection_name
        # Set up logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig()
        self.logger.info("Initializing RAPTOR with collection_name: %s", collection_name)

        start_time = time.time()

        try:
            self.client = chromadb.PersistentClient(path="chroma_db")
            
            if force_rebuild:
                self.logger.info("Force rebuilding collection...")
                self.client.delete_collection(collection_name)

            self.collection = self.client.get_or_create_collection(collection_name)
            
            self.vector_store = ChromaVectorStore(chroma_collection=self.collection)

            self.logger.info("Loading provided documents...")
            self.documents = SimpleDirectoryReader(input_files=files).load_data()
            
            if force_rebuild or len(os.listdir("chroma_db")) == 1:
                self.retriever = self.build_raptor_tree()
            else:
                self.retriever = self.setup_retriever()
                
            self.query_engine = self.setup_query_engine()
        except Exception as e:
            self.logger.error("An error occurred during initialization: %s", e)
            raise

        end_time = time.time()
        setup_duration = end_time - start_time
        self.logger.info("RAPTOR setup completed in %s seconds", setup_duration)

    def build_raptor_tree(self):
        try:
            self.logger.info("Creating RaptorPack and building raptor tree...")
            raptor_pack = RaptorPack(
                self.documents,
                embed_model=OpenAIEmbedding(model=EMBEDDING_MODEL),  # used for embedding clusters
                llm=OpenAI(model=LLM_settings, temperature=0.1, api_key=st.session_state["openai_api_key"]), 
                vector_store=self.vector_store,
                similarity_top_k=SIMILARITY_TOP_K,
                mode=RETRIEVAL_METHOD, 
            )
            modules = raptor_pack.get_modules()
            return modules["retriever"]
        except Exception as e:
            self.logger.error("An error occurred while building raptor tree: %s", e)
            raise

    def setup_retriever(self):
        try:
            self.logger.info("Setting up RaptorRetriever")
            return RaptorRetriever(
                [],
                embed_model=OpenAIEmbedding(model=EMBEDDING_MODEL),  # used for embedding clusters
                llm=OpenAI(model=LLM_settings, temperature=0.1, api_key=st.session_state["openai_api_key"]), # used for generating summaries
                vector_store=self.vector_store,
                similarity_top_k=SIMILARITY_TOP_K,
                mode=RETRIEVAL_METHOD, 
            )
        except Exception as e:
            self.logger.error("An error occurred while setting up RaptorRetriever: %s", e)
            raise

    def setup_query_engine(self):
        try:
            self.logger.info("Setting up RetrieverQueryEngine")
            return RetrieverQueryEngine.from_args(
                self.retriever, llm=OpenAI(model=LLM_settings, temperature=0.1, api_key=st.session_state["openai_api_key"])
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

def get_raptor(files, force_rebuild=False):
    velociraptor = RAPTOR(files=files, collection_name="pjs", force_rebuild=force_rebuild)
    return velociraptor
