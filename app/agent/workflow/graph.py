import logging
from langgraph.graph import StateGraph, START, END
from app.agent.state import AgentState
from app.agent.planner.nodes.planner_node import planner
from app.agent.planner.nodes.executor_node import executor
from app.agent.workflow.prompts.synthesis_prompt import SYNTHESIS_PROMPT
from app.infra.llm import getLLM
from app.agent.planner.nodes.replanner_node import replanner_node
from app.agent.critic.critic_node import critic_node
from app.agent.workflow.edges import route_after_critic, route_after_executor, route_after_planner, route_after_replanner

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)


def recusa(state: AgentState) -> dict:
    return {"answer": "Desculpe, esta solicitação está fora do meu domínio."}


def synthesis(state: AgentState) -> dict:
    llm = getLLM()
    print("🟢 [3/4] Sintetizando resposta final...")
    synthesizer = SYNTHESIS_PROMPT | llm
    res = synthesizer.invoke({
        "question": state["question"],
        "sql_evidence": state.get("sql_evidence"),
        "rag_evidence": state.get("rag_evidence")
    })
    return {"answer": res.content}





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





