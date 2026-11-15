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
    sql_evidence = state.get("sql_evidence")
    rag_evidence = state.get("rag_evidence")

    print(f"🔵 [2/4] Executando passo {step.step_id}: {step.action}...")

    if step.action == StepAction.SQL:
        result = _run_sql(step, state)
        observations[step.step_id] = result
        sql_evidence = result

    elif step.action == StepAction.QDRANT:
        result = _run_qdrant(step, state)
        observations[step.step_id] = result
        rag_evidence = result

    return {
        "current_step_index": idx + 1,
        "completed_steps": state.get("completed_steps", []) + [step.step_id],
        "observations": observations,
        "sql_evidence": sql_evidence,
        "rag_evidence": rag_evidence
    }


if __name__ == "__main__":
    import traceback
    from app.agent.planner.schemas import Plan, PlanStep

    # 1. Cria um plano simulado (como se tivesse vindo do nó planner)
    plano_exemplo = Plan(
        reasoning="Plano de teste: primeiro busca os dados no banco SQL",
        steps=[
            PlanStep(
                step_id=1,
                action=StepAction.SQL,
                description="Buscar tickets com status aberto",
                depends_on=[]
            ),
            PlanStep(
                step_id=2,
                action=StepAction.SYNTHESIZE,
                description="Sintetizar a resposta",
                depends_on=[1]
            )
        ]
    )

    # 2. Monta o estado inicial que o executor espera receber
    estado_inicial: AgentState = {
        "question": "Quantos tickets abertos existem atualmente?",
        "plan": plano_exemplo,
        "current_step_index": 0,
        "completed_steps": [],
        "observations": {},
        "sql_evidence": None,
        "rag_evidence": None,
        "answer": ""
    }

    try:
        print("--- Executando o primeiro passo do plano com o executor() ---")
        resultado_parcial = executor(estado_inicial)

        print("\n✅ Passo executado com sucesso!")
        print("Próximo índice de passo (current_step_index):", resultado_parcial["current_step_index"])
        print("Passos concluídos:", resultado_parcial["completed_steps"])
        print("Evidência SQL capturada:", resultado_parcial["sql_evidence"])
    except Exception as e:
        print("\n❌ ERRO DETECTADO:")
        traceback.print_exc()