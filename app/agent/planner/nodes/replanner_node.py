from app.agent.state import AgentState
from app.agent.llm import getLLM
from app.agent.planner.prompts import REPLANNER_PROMPT
from app.agent.planner.schemas import Plan

def replanner_node(state: AgentState)-> dict:
    question = state["question"]
    previous_plan = state["plan"]
    completed_steps = state.get("completed_steps", [])
    observations = state.get("observations", {})
    errors = state.get("errors", {})
    replan_count = state.get("replan_count", 0)


    print(f"🔄 [Replanner] Replanejando (tentativa {replan_count + 1})...")
    llm = getLLM()
    structured = llm.with_structured_output(Plan)
    chain = REPLANNER_PROMPT | structured

    new_plan = chain.invoke({
        "question": question,
        "previous_plan": previous_plan,
        "completed_steps": completed_steps,
        "observations": observations,
        "errors": errors,
        "replan_count": replan_count,
    })

    return {
            "plan": new_plan,
            "current_step_index": 0,
            "replan_count": replan_count + 1,
            "failed_steps": []
        }






