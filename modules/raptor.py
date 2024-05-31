import os
import chromadb
import streamlit as st

from llama_index.core import SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.packs.raptor import RaptorPack, RaptorRetriever

if "openai_api_key" not in st.session_state:
    st.session_state.openai_api_key = os.getenv('OPENAI_API_KEY')

embed_model = OpenAIEmbedding(embed_batch_size=10, api_key=st.session_state.openai_api_key)
Settings.embed_model = embed_model

class RAPTORRetriever:
    def __init__(self, documents_path, db_path, collection_name):
        self.documents_path = documents_path
        self.db_path = db_path
        self.collection_name = collection_name
        self.vector_store = self.initialize_vector_store()
        self.documents = self.load_documents()
        self.raptor_pack = self.create_raptor_pack()

    def load_documents(self):
        reader = SimpleDirectoryReader(input_files=[self.documents_path])
        return reader.load_data()

    def initialize_vector_store(self):
        client = chromadb.PersistentClient(path=self.db_path)
        collection = client.get_or_create_collection(self.collection_name)
        return ChromaVectorStore(chroma_collection=collection)

    def create_raptor_pack(self):
        return RaptorPack(
            self.documents,
            embed_model=embed_model,
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1),
            vector_store=self.vector_store,
            similarity_top_k=2,
            mode="collapsed",
            transformations=[SentenceSplitter(chunk_size=400, chunk_overlap=50)],
        )

    def retrieve_nodes(self, query, mode="collapsed"):
        return self.raptor_pack.run(query, mode=mode)

    def initialize_retriever(self, mode="tree_traversal"):
        return RaptorRetriever(
            [],
            embed_model=embed_model,
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1),
            vector_store=self.vector_store,
            similarity_top_k=2,
            mode=mode,
        )


    def query(self, query_text, mode="tree_traversal"):
        retriever = self.initialize_retriever(mode=mode)
        query_engine = self.create_query_engine(retriever)
        return query_engine.query(query_text)

if __name__ == "__main__":
    # Check if persisted data exists
    persist_path = "./persist"
    if os.path.exists(persist_path):
        retriever = RaptorRetriever.from_persist_dir(
            persist_path,
            embed_model=embed_model,
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1),
            vector_store=ChromaVectorStore(chroma_collection=chromadb.PersistentClient(path="./raptor_paper_db").get_or_create_collection("raptor")),
            similarity_top_k=2,
            mode="tree_traversal",
        )
    else:
        retriever = RAPTORRetriever(
            documents_path="./raptor_paper.pdf",
            db_path="./raptor_paper_db",
            collection_name="raptor"
        )

    nodes_collapsed = retriever.retrieve_nodes("What baselines is raptor compared against?", mode="collapsed")
    print(len(nodes_collapsed))
    print(nodes_collapsed[0].text)

    nodes_tree_traversal = retriever.retrieve_nodes("What baselines is raptor compared against?", mode="tree_traversal")
    print(len(nodes_tree_traversal))
    print(nodes_tree_traversal[0].text)
