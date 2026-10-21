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