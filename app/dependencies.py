from app.services.interfaces.chat_service_interface import IChatService
from app.services.chat_service import ChatService
from app.agent.workflow.graph import get_planner_graph
from functools import lru_cache
from fastapi import Depends
from langgraph.graph.state import CompiledStateGraph

@lru_cache(maxsize=1)
def get_compiled_state_graph() -> CompiledStateGraph:
    return get_planner_graph()

def get_chat_service(agent: CompiledStateGraph  = Depends(get_compiled_state_graph)) -> IChatService:
    planner_agent = get_planner_graph()
    return ChatService(agent=planner_agent)