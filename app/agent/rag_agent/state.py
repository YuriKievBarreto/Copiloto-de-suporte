from typing import TypedDict, Any
from langchain_core.documents import Document
MAX_ATTEMPTS = 3
from enum import StrEnum

class Status(StrEnum):
    RUNNING = "running"
    FAILED = "failed"
    SUCCESS = "success"


class RAGAgentState(TypedDict):
    question: str
    search_query: str
    queries_tried: list[str]
    feedback: str
    documents: list[Document]
    is_relevant: bool
    attempts: int
    status: Status





def initial_rag_state(question: str) -> RAGAgentState:
    return {
        "question": question,
        "search_query": "",
        "queries_tried": [],
        "feedback": "",
        "documents": [],
        "is_relevant": False,
        "attempts": 0,
        "status": Status.RUNNING,
    }