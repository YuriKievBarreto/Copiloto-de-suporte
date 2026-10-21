from typing import TypedDict, Any
from langchain_core.documents import Document
MAX_ATTEMPTS = 3
from enum import StrEnum

class Status(StrEnum):
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