from langgraph.graph import StateGraph
from typing import TypedDict
from enum import StrEnum

class Routes(StrEnum):
    SQL = "sql"
    QDRANT = "qdrant"
    BOTH = "both"
    OUT_OF_SCOPE = "out_of_scope"



class RouterState(TypedDict):
    question: str
    route: Routes
    route_reason: str
    sql_evidence: str
    rag_evidence: str
    answer: str