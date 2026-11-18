from functools import lru_cache
from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph

from app.services.interfaces.chat_service_interface import IChatService
from app.services.chat_service import ChatService
from app.agent.workflow.graph import get_planner_graph


@lru_cache(maxsize=1)
def get_compiled_planner_graph() -> CompiledStateGraph:
    """Compila o grafo do LangGraph apenas uma vez (Singleton)."""
    return get_planner_graph()


def get_chat_service(
    agent: CompiledStateGraph = Depends(get_compiled_planner_graph),
) -> IChatService:
    """Injeta o grafo compilado no ChatService por requisição."""
    return ChatService(agent=agent)
