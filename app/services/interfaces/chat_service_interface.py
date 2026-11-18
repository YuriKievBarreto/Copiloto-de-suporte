from typing import Protocol
from app.schemas.chat_schemas import ChatRequest, ChatResponse


class IChatService(Protocol):
    async def chat(self, data: ChatRequest) -> ChatResponse | None:
        ...