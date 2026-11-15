from app.agent.llm import getLLM, getGROQLLM
from app.agent.planner.schemas import Plan
from app.agent.planner.prompts import PLANNER_PROMPT
from app.agent.state import AgentState


def planner(state: AgentState) -> dict:
    print("🟡 [1/4] Iniciando Planner...")
    llm = getGROQLLM()
    structured = llm.with_structured_output(Plan)
    chain = PLANNER_PROMPT | structured
    plan: Plan = chain.invoke({"question": state["question"]})
    return {
        "plan": plan,
        "current_step_index": 0,
        "completed_steps": [],
        "observations": {},
        "sql_evidence": None,
        "rag_evidence": None
    }


