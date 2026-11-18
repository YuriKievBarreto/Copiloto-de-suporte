from langchain_core.documents import Document
from qdrant_client import models
from app.infra.database.vector_database import get_vector_store
from app.agent.rag_agent.state import RAGAgentState

vector_store = get_vector_store()

def retrieve(state: RAGAgentState) -> dict:
    category = state.get("category")

    query_filter = None
    if category:
        query_filter = models.Filter(
            must=[
                models.FieldCondition(
                    key="metadata.categoria",
                    match=models.MatchValue(value=category),
                )
            ]
        )

    docs = vector_store.similarity_search(
        state["search_query"],
        k=5,
        filter=query_filter,
    )

    return {
        "documents": docs,
        "attempts": state.get("attempts", 0) + 1,
    }
    
