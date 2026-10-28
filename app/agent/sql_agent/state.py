from typing import TypedDict, Any
from enum import Enum
class Status(Enum):
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"

MAX_ATTEMPTS = 3

class SQLAgentState(TypedDict):
    question: str
    sql: str
    result: list[dict[str, Any]] | None
    error: str | None
    attempts: int


def initial_sql_state(question: str) -> SQLAgentState:
    return {
        "question": question,
        "sql": "",
        "result": None,
        "error": None,
        "attempts": 0,
    }