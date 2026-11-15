from typing import TypedDict, Optional, Any
from app.agent.planner.schemas import Plan


class AgentState(TypedDict):
    question: str
    plan: Optional[Plan]
    current_step_index: int
    completed_steps: list[int]
    observations: dict[int, Any]
    sql_evidence: Optional[dict]
    rag_evidence: Optional[dict]
    answer: str
