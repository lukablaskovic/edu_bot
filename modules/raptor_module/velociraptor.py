import os
import streamlit as st
import fitz
from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

from modules.raptor_module.raptor_impl import RetrievalAugmentation



if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = ""


def process_or_load_raptor(file_path):
 
    save_path = f"raptor_trees/test" 
    if os.path.exists(save_path):
        # Load existing RAPTOR structure
        RA = RetrievalAugmentation(tree=save_path)
        
    else:
        reader = SimpleDirectoryReader(file_path)
        docs = reader.load_data()
        print(f"Loaded {len(docs)} docs")
        text = docs[0].text
        RA = RetrievalAugmentation()
        RA.add_documents(text)
        RA.save("raptor_trees/test")
    return RA
