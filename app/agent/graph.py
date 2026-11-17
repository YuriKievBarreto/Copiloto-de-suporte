import logging
from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.planner.nodes.planner_node import planner
from app.agent.planner.nodes.executor_node import executor
from app.agent.prompts.synthesis_prompt import SYNTHESIS_PROMPT
from app.agent.llm import getLLM
from app.agent.planner.nodes.replanner_node import replanner_node
from app.agent.critic.critic_node import critic_node

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

llm = getLLM()

MAX_REPLANS = 2
MAX_CRITIC_REPLANS = 2

def route_after_planner(state: AgentState) -> str:
    plan = state["plan"]
    if plan.out_of_scope:
        return "recusa"
    return "executor"


def route_after_executor(state: AgentState) -> str:
    plan = state["plan"]
    idx = state["current_step_index"]

    failed_steps = state.get("failed_steps") or []
    replan_count = state.get("replan_count") or 0
    if failed_steps:
        if replan_count < MAX_REPLANS:
            return "replanner"
        else:
            return "synthesis"


    steps = plan.steps
    if idx >= len(steps):
        return "synthesis"
    next_step = steps[idx]
    if next_step.action.upper() == "SYNTHESIZE":
        return "synthesis"
    return "executor"



def route_after_replanner(state: AgentState):
    plan = state["plan"]
    if plan.out_of_scope:
        return "recusa"
    return "executor"


def recusa(state: AgentState) -> dict:
    return {"answer": "Desculpe, esta solicitação está fora do meu domínio."}


def synthesis(state: AgentState) -> dict:
    print("🟢 [3/4] Sintetizando resposta final...")
    synthesizer = SYNTHESIS_PROMPT | llm
    res = synthesizer.invoke({
        "question": state["question"],
        "sql_evidence": state.get("sql_evidence"),
        "rag_evidence": state.get("rag_evidence")
    })
    return {"answer": res.content}


def route_after_critic(state: AgentState):
    passed = state.get("passed", False)
    print("PASSOU????? ", passed)
    critic_replan_count = state.get("critic_replan_count", 0)
    replan_count = state.get("replan_count", 0)

    if passed:
        return "END"
    if critic_replan_count >= MAX_CRITIC_REPLANS or replan_count >= MAX_REPLANS:
        return "END"  
    return "replanner"



def get_planner_graph():
    builder = StateGraph(AgentState)

    builder.add_node("planner", planner)
    builder.add_node("executor", executor)
    builder.add_node("recusa", recusa)
    builder.add_node("synthesis_node", synthesis)
    builder.add_node("replanner", replanner_node)
    builder.add_node("critic", critic_node)
    builder.add_edge(START, "planner")
    
    builder.add_conditional_edges(
        "planner",
        route_after_planner,
        {"recusa": "recusa", "executor": "executor"}
    )

    builder.add_conditional_edges(
        "executor",
        route_after_executor,
        {"executor": "executor", "synthesis": "synthesis_node", "replanner": "replanner"}
    )

    builder.add_conditional_edges(
        "replanner",
        route_after_replanner,
        {"executor": "executor", "synthesis": "synthesis_node", "recusa": "recusa"}
    )

    builder.add_conditional_edges(
        "critic",
        route_after_critic,
        {"END": END, "replanner": "replanner"}
    )

    builder.add_edge("recusa", END)
    builder.add_edge("synthesis_node", "critic")

    return builder.compile()


# Alias para manter compatibilidade
def get_router_graph():
    return get_planner_graph()


if __name__ == "__main__":
    import traceback
    p_graph = get_planner_graph()
    print(p_graph.get_graph().draw_mermaid())
    try:
        print("cheguei aqiu")
        res = p_graph.invoke({"question": "quantos usuarios por cada categoria de plano?"})
        print("repostas::;")
        print("\nRESPOSTA:\n", res["answer"])
    except Exception as e:
        print("\n❌ ERRO DETECTADO:")
        traceback.print_exc()
