from langgraph.graph import StateGraph, START , END
from app.agent.rag_agent.state import RAGAgentState, Status, MAX_ATTEMPTS
from app.agent.rag_agent.nodes import grade, analyze_query, retrieve_node, rewrite_query

def finalize_success(state: RAGAgentState) -> dict:
    return {"status": Status.SUCCESS}

def finalize_failed(state: RAGAgentState) -> dict:
    return {"status": Status.FAILED}



def route_after_grade(state: RAGAgentState) -> str:
    if state["is_relevant"]:
        return "success"
    if state["attempts"] >= MAX_ATTEMPTS:
        return "failed"
    return "rewrite"



def get_rag_agent_graph():
    builder = StateGraph(RAGAgentState)

    builder.add_node("grade", grade.grade)
    builder.add_node("analyze_query", analyze_query.analyze_query)
    builder.add_node("retrieve", retrieve_node.retrieve)
    builder.add_node("rewrite", rewrite_query.rewrite_query)
    builder.add_node("success", finalize_success)
    builder.add_node("failed", finalize_success)

    builder.add_edge(START, "analyze_query")
    builder.add_edge("analyze_query", "retrieve")
    builder.add_edge("retrieve", "grade")
    builder.add_conditional_edges(
        "grade",
        route_after_grade,
        {"success": "success", "failed": "failed", "rewrite": "rewrite"},

    )

    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("success", END)
    builder.add_edge("failed", END)

    rag_agent_graph = builder.compile()
    return rag_agent_graph