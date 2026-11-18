from app.agent.state import AgentState
from app.infra.llm import getLLM
from app.agent.critic.prompts import critic_prompt
from app.agent.critic.schemas import CriticEvaluation

def critic_node(state: AgentState):
    llm = getLLM()
    critic_chain =  critic_prompt | llm.with_structured_output(CriticEvaluation)

    res: CriticEvaluation = critic_chain.invoke({
        "question": state["question"],
        "sql_evidence": state.get("sql_evidence") or "Sem evidência SQL",
        "rag_evidence": state.get("rag_evidence") or "Sem evidencia RAG",
        "answer": state.get("answer")
    })

    

    passed = res.is_grounded and res.is_complete
    feedback = None
    if not passed:
        feedback = res.needed_action or  res.critique
    return {
        "critic_evaluation": res.model_dump(),
        "critic_feedback": feedback,
        "passed": passed,
    }