from app.agent.state import AgentState
from app.agent.state import AgentState
from app.agent.planner.schemas import StepAction, PlanStep
from app.agent.sql_agent.graph import get_sql_agent_graph
from app.agent.sql_agent.state import initial_sql_state
from app.agent.rag_agent.graph import get_rag_agent_graph
from app.agent.rag_agent.state import initial_rag_state, Status as RagStatus
import logging
import time
logger = logging.getLogger(__name__)

sql_graph = get_sql_agent_graph()
rag_graph = get_rag_agent_graph()


def _build_context(step: PlanStep, observations: dict) -> str:
    if not step.depends_on:
        return ""
    parts = []
    for dep_id in step.depends_on:
        obs = observations.get(dep_id)
        if obs:
            parts.append(f"[Resultado do passo {dep_id}: {obs}]")

    return "\n".join(parts)


def _run_sql(step: PlanStep, state: AgentState) -> dict:
    context = _build_context(step, state["observations"])
    question_with_context = state["question"]
    if context:
        question_with_context = f"{question_with_context}\n\n Contexto adicional: \n {context}"

    try:
        res = sql_graph.invoke(initial_sql_state(question_with_context))
        
        ok = res.get("error") is None and res.get("result") is not None
        return {
            "status": "success" if ok else "failed",
            "sql": res.get("sql"),
            "rows": res.get("result") or [],
            "error": res.get("error"),
        }
    except Exception as e:
        logger.exception("Executor: falha no SQL Agent")
        return {"status": "failed", "sql": None, "rows": [], "error": str(e)}


def _run_qdrant(step: PlanStep, state: AgentState) -> dict:
    context = _build_context(step, state["observations"])
    question_with_context = state["question"]
    if context:
        question_with_context = f"{question_with_context}\n\nContexto adicional:\n{context}"
    try:
        res = rag_graph.invoke(initial_rag_state(question_with_context))
        ok = res.get("status") == RagStatus.SUCCESS
        return {
            "status": "success" if ok else "failed",
            "documents": res.get("documents") or [],
            "error": None if ok else "não foi possível recuperar documentos relevantes",
        }
    except Exception as e:
        logger.exception("Executor: falha no RAG Agent")
        return {"status": "failed", "documents": [], "error": str(e)}


def executor(state: AgentState) -> dict:
    
    plan = state["plan"]
    idx = state["current_step_index"]
    steps = plan.steps
    

    if idx >= len(steps):
        return {}  

    step = steps[idx]
    observations = dict(state.get("observations") or {})
    errors = dict(state.get("errors") or {})
    failed_steps = list(state.get("failed_steps") or [])
    completed_steps = list(state.get("completed_steps") or [])

    sql_evidence = state.get("sql_evidence")
    rag_evidence = state.get("rag_evidence")

    print(f"🔵 [2/4] Executando passo {step.step_id}: {step.action}...")

    if step.action == StepAction.SQL:
        result = _run_sql(step, state)
        if result.get("status") == "failed":
            errors[step.step_id] = result["error"]
            failed_steps.append(step.step_id)

        else:
            completed_steps.append(step.step_id)

        observations[step.step_id] = result
        sql_evidence = result
       

    elif step.action == StepAction.QDRANT:
        result = _run_qdrant(step, state)
        if result.get("status") == "failed":
            errors[step.step_id] = result["error"]
            failed_steps.append(step.step_id)

        else:
            completed_steps.append(step.step_id)


        observations[step.step_id] = result
        rag_evidence = result

    return {
        "current_step_index": idx + 1,
        "completed_steps": completed_steps,
        "observations": observations,
        "sql_evidence": sql_evidence,
        "rag_evidence": rag_evidence,
        "errors": errors,
        "failed_steps": failed_steps
    }


