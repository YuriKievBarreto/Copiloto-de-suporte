from langgraph.graph import END, StateGraph, START
from app.agent.sql_agent.state import SQLAgentState, MAX_ATTEMPTS
from app.agent.sql_agent.nodes import generate_sql, execute_sql

def route(state: SQLAgentState) -> str:
    if state["error"] is None:
        return "fim"

    if state["attempts"] >= MAX_ATTEMPTS:
        return "fim"

    return "tentar_de_novo"


def get_sql_agent_graph():
    builder = StateGraph(SQLAgentState)

    builder.add_node("generate_sql", generate_sql.generate_sql_node)
    builder.add_node("execute_sql", execute_sql.execute_sql)

    builder.add_edge("generate_sql", "execute_sql")
    builder.add_edge(START, "generate_sql")
    builder.add_conditional_edges(
        "execute_sql",
        route,
        {"fim": END, "tentar_de_novo": "generate_sql"}
    )

    graph = builder.compile()
    return graph


