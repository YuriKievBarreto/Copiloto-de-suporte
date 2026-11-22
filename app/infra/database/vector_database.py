from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance
from langchain_aws import BedrockEmbeddings
from app.core.config import get_settings

settings = get_settings()

embeddings = BedrockEmbeddings(
    model_id=settings.embedding_model,
    region_name=settings.aws_region,
    aws_access_key_id=settings.aws_access_key_id.get_secret_value() if settings.aws_access_key_id else None,
    aws_secret_access_key=settings.aws_secret_access_key.get_secret_value() if settings.aws_secret_access_key else None,
    dimensions=1024,
    normalize=True,
)

collection_name = settings.qdrant_collection


def get_vector_store():
    api_key = settings.qdrant_api_key.get_secret_value() if settings.qdrant_api_key else None
    client = QdrantClient(
        url=settings.effective_qdrant_url,
        api_key=api_key,
    )

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

    return vector_store
