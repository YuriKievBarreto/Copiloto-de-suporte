from langgraph.graph import StateGraph, START, END
from app.agent.state import RouterState, Routes
from app.agent.sql_agent.graph import get_sql_agent_graph
from app.agent.rag_agent.graph import get_rag_agent_graph
from app.agent.sql_agent.state import initial_sql_state
from app.agent.rag_agent.state import initial_rag_state, Status as RagStatus
from app.agent.prompts.routing_prompt import SYSTEM_PROMPT
from app.agent.prompts.synthesis_prompt import SYNTHESIS_PROMPT
from app.agent.llm import getLLM
from pydantic import Field, BaseModel
import logging


logger = logging.getLogger(__name__)



sql_graph = get_sql_agent_graph()
rag_graph = get_rag_agent_graph()
llm = getLLM()

def format_docs(docs) -> str:
    return "\n\n".join(
        f"[{i}] ({d.metadata.get('categoria')}) {d.metadata.get('titulo')}\n{d.page_content}"
        for i, d in enumerate(docs, start=1)
    )



class RoutingOutput(BaseModel):
    route_reason: str = Field(description="descreva em poucas frases o motivo da escolha da rota")
    route: Routes


def router(state: RouterState):
    router = llm.with_structured_output(RoutingOutput)
    chain = SYSTEM_PROMPT | router
    res: RoutingOutput = chain.invoke({"question": state["question"]})
    route_reason = res.route_reason
    route = res.route

    return {"route": route, "route_reason": route_reason}


def router_result(state: RouterState):
    chosen_route = state["route"]
    print("---------------ROTA ESCOLHIDA----------------------")
    print(chosen_route)
    if chosen_route.lower() != "both":
        return chosen_route.lower()
    return ["sql", "qdrant"]

def recusa(state: RouterState):
    return {"answer": "Desculpe, esta solicitação está fora do meu domínio."}


def sql_agent(state: RouterState):
    try:
        res = sql_graph.invoke(initial_sql_state(state["question"]))
        error = res.get("error")
        result = res.get("result")
        ok = error is None and result is not None
        return {
            "sql_evidence": {
                "status": "success" if ok else "failed",
                "sql": res.get("sql"),
                "rows": result or [],
                "error": error or (None if ok else "sem resultado após as tentativas"),
            }
        }
    except Exception as e:
        logger.exception("falha no SQL Agent")
        return {"sql_evidence": {"status": "failed", "sql": None, "rows": [], "error": str(e)}}


def rag_agent(state: RouterState):
    try:
        res = rag_graph.invoke(initial_rag_state(state["question"]))
        ok = res.get("status") == RagStatus.SUCCESS
        return {
            "rag_evidence": {
                "status": "success" if ok else "failed",
                "documents": res.get("documents") or [],
                "error": None if ok else "não foi possível recuperar documentos relevantes",
            }
        }
    except Exception as e:
        logger.exception("falha no RAG Agent")
        return {"rag_evidence": {"status": "failed", "documents": [], "error": str(e)}}



def synthesis(state: RouterState):
    synthesizer = SYNTHESIS_PROMPT | llm
    res = synthesizer.invoke({"question": state["question"], "sql_evidence": state["sql_evidence"], "rag_evidence": state["rag_evidence"]})
    answer = res.content
    return {"answer": answer}

def get_router_graph():
    builder = StateGraph(RouterState)

    builder.add_node("sql_agent_node", sql_agent)
    builder.add_node("rag_agent_node", rag_agent)
    builder.add_node("recusa", recusa)
    builder.add_node("classify", router)
    builder.add_node("synthesis_node", synthesis)
    builder.add_edge(START, "classify")
    builder.add_edge("sql_agent_node","synthesis_node")
    builder.add_edge("rag_agent_node", "synthesis_node")
    builder.add_conditional_edges("classify", router_result, {"sql": "sql_agent_node", "qdrant": "rag_agent_node", "out_of_scope": "recusa"})
    builder.add_edge("synthesis_node", END)

    graph = builder.compile()
    return graph


if __name__ == "__main__":
    r_graph  = get_router_graph()
    res = r_graph.invoke({"question": "Temos agentes sênior com tickets críticos em aberto? Liste os nomes."})
    print(res)