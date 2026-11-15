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


if __name__ == "__main__":
    import traceback

    # Estado de entrada contendo a pergunta do usuário
    estado_teste: AgentState = {
        "question": """O cliente do ticket 103 está reclamando de erro de taxa de requisições na API. Descubra no banco qual é o plano desse cliente e consulte na
  │     documentação qual é o limite de requisições por minuto permitido para ele.""",
        "plan": None,
        "current_step_index": 0,
        "completed_steps": [],
        "observations": {},
        "sql_evidence": None,
        "rag_evidence": None,
        "answer": ""
    }

    try:
        print("--- Executando o nó planner() diretamente ---")
        saida = planner(estado_teste)
        plano = saida["plan"]

        print("\n✅ Plano gerado com sucesso pelo LLM!")
        print(f"Raciocínio: {plano.reasoning}")
        print(f"Fora de escopo? {plano.out_of_scope}")
        print(f"Total de passos: {len(plano.steps)}")
        print("\nPassos do plano:")
        for step in plano.steps:
            deps = f"(depende de: {step.depends_on})" if step.depends_on else ""
            print(f"  👉 Passo {step.step_id} [{step.action}]: {step.description} {deps}")

    except Exception as e:
        print("\n❌ ERRO DETECTADO NO PLANNER:")
        traceback.print_exc()
