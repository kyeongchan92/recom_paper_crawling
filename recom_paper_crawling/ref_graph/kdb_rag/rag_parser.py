from llama_parse import LlamaParse
from llama_index.core import Settings
from llama_index.core import StorageContext
from llama_index.core import VectorStoreIndex
from llama_index.core.node_parser import MarkdownElementNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.vector_stores.kdbai import KDBAIVectorStore
from getpass import getpass
import kdbai_client as kdbai

from dotenv import load_dotenv
import os

load_dotenv()


from openai import OpenAI

client = OpenAI()


class RagParser:
    def __init__(self):
        self.session = kdbai.Session(
            api_key=os.environ["KDBAI_API_KEY"], endpoint=os.environ["KDBAI_ENDPOINT"]
        )
        self.db = self.session.database("default")

        # The schema contains two metadata columns (document_id, text) and one embeddings column
        # schema = [
        #     dict(name="document_id", type="str"),
        #     dict(name="text", type="str"),
        #     dict(name="embeddings", type="float32s"),
        # ]

        # # indexflat, define the index name, type, column to apply the index to (embeddings)
        # # and params which include thesearch metric (Euclidean distance), and dims
        # indexFlat = {
        #     "name": "flat",
        #     "type": "flat",
        #     "column": "embeddings",
        #     "params": {"dims": 1536, "metric": "L2"},
        # }

        # KDBAI_TABLE_NAME = "LlamaParse_Table"

        # # First ensure the table does not already exist
        # try:
        #     self.db.table(KDBAI_TABLE_NAME).drop()
        # except kdbai.KDBAIException:
        #     pass

        # # Create the table
        # self.table = self.db.create_table(
        #     table=KDBAI_TABLE_NAME, schema=schema, indexes=[indexFlat]
        # )

        # self.EMBEDDING_MODEL = "text-embedding-3-small"
        # self.GENERATION_MODEL = "gpt-4o"

        # self.llm = OpenAI(model=self.GENERATION_MODEL)
        # self.embed_model = OpenAIEmbedding(model=self.EMBEDDING_MODEL)

        # Settings.llm = self.llm
        # Settings.embed_model = self.embed_model

    def parse(self, pdf_file_name):
        documents = LlamaParse(
            result_type="markdown",
            # parsing_instructions=parsing_instructions
        ).load_data(pdf_file_name)

        # Parse the documents using MarkdownElementNodeParser
        node_parser = MarkdownElementNodeParser(
            llm=self.llm, num_workers=8
        ).from_defaults()

        # Retrieve nodes (text) and objects (table)
        nodes = node_parser.get_nodes_from_documents(documents)

        base_nodes, objects = node_parser.get_nodes_and_objects(nodes)

        vector_store = KDBAIVectorStore(self.table)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)

        # Create the index, inserts base_nodes and objects into KDB.AI
        self.recursive_index = VectorStoreIndex(
            nodes=base_nodes + objects, storage_context=storage_context
        )

    def embed_query(self, query):
        query_embedding = client.embeddings.create(
            input=query, model="text-embedding-3-small"
        )
        return query_embedding.data[0].embedding

    def retrieve_data(self, query):
        query_embedding = self.embed_query(query)
        results = self.table.search(
            vectors={"flat": [query_embedding]},
            n=5,
            filter=[("<>", "document_id", "4a9551df-5dec-4410-90bb-43d17d722918")],
        )
        retrieved_data_for_RAG = []
        for index, row in results[0].iterrows():
            retrieved_data_for_RAG.append(row["text"])
        return retrieved_data_for_RAG

    def RAG(query):
        question = (
            "You will answer this question based on the provided reference material: "
            + query
        )
        messages = "Here is the provided context: " + "\n"
        results = self.retrieve_data(query)
        if results:
            for data in results:
                messages += data + "\n"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": question},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": messages},
                    ],
                },
            ],
            # max_tokens=300,
        )
        content = response.choices[0].message.content
        return content

