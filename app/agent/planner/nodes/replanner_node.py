from app.agent.state import AgentState
from app.agent.events import emit, classify_error, redact_sql
from app.infra.llm import getLLM
from app.agent.planner.prompts import REPLANNER_PROMPT
from app.agent.planner.schemas import Plan

def replanner_node(state: AgentState)-> dict:
    question = state["question"]
    previous_plan = state["plan"]
    completed_steps = state.get("completed_steps", [])
    observations = state.get("observations", {})
    errors = state.get("errors", {})
    replan_count = state.get("replan_count", 0)

    critic_replan_count = state.get("critic_replan_count", 0)

    critic_feedback = state.get("critic_feedback")
    triggered_by_critic = bool(critic_feedback)

    origem = "critic" if triggered_by_critic else "falha de execução"
    print(f"🔄 [Replanner] Replanejando (tentativa {replan_count + 1}, origem: {origem})...")

    if triggered_by_critic:
        reason = redact_sql(critic_feedback)
    else:
        kinds = sorted({classify_error(e) for e in errors.values()})
        reason = "Falha na execução dos passos: " + (", ".join(kinds) or "unknown")
    emit("replan", attempt=replan_count + 1, origin="critic" if triggered_by_critic else "execution", reason=reason)

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
        "critic_feedback": critic_feedback or "Nenhum",

    })

    

    return {
            "plan": new_plan,
            "current_step_index": 0,
            "replan_count": replan_count + 1,
            "critic_replan_count": critic_replan_count + (1 if triggered_by_critic else 0),
            "critic_feedback": None,
            "failed_steps": []
        }






