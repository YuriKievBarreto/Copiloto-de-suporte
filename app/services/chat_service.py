from app.services.interfaces.chat_service_interface import IChatService
from app.schemas.chat_schemas import ChatResponse, ChatRequest
from langgraph.graph.state import CompiledStateGraph


class ChatService(IChatService):
    def __init__(self, agent: CompiledStateGraph) -> None:
        self.agent = agent

    async def chat(self, data: ChatRequest) -> ChatResponse:
        res = await self.agent.ainvoke({"question": data.input})
        return ChatResponse(answer=res["answer"])
