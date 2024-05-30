class RAPTORRetriever:
    def __init__(self, documents_path, db_path, collection_name):
        self.documents_path = documents_path
        self.db_path = os.path.join("chroma_dbs", db_path)  # Embeddings folder
        self.collection_name = collection_name
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
        self.documents = self.load_documents()
        self.vector_store = self.initialize_vector_store()
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
            embed_model=OpenAIEmbedding(model="text-embedding-3-small"),
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
            embed_model=OpenAIEmbedding(model="text-embedding-3-small"),
            llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1),
            vector_store=self.vector_store,
            similarity_top_k=2,
            mode=mode,
        )

    def create_query_engine(self, retriever):
        return RetrieverQueryEngine.from_args(
            retriever, llm=OpenAI(model="gpt-3.5-turbo", temperature=0.1)
        )

    def query(self, query_text, mode="tree_traversal"):
        retriever = self.initialize_retriever(mode=mode)
        query_engine = self.create_query_engine(retriever)
        return query_engine.query(query_text)

if __name__ == "__main__":
    raptor_retriever = RAPTORRetriever(
        documents_path='./uploaded_files/PJS1.pdf',
        db_path='./raptor_db',
        collection_name='raptor_collection'
    )
    nodes = raptor_retriever.retrieve_nodes("What baselines is raptor compared against?", mode="collapsed")
    print(len(nodes))
    print(nodes[0].text)
