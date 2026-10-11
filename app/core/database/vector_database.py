from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import os
load_dotenv()

embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": True, "batch_size": 8},
)

collection_name = "manuais"


client = QdrantClient(url="http://localhost:6333")

if not client.collection_exists(collection_name):
    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=1024,
            distance=Distance.COSINE
        )
    )

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings
)