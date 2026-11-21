from typing import AsyncIterator, Protocol
from app.schemas.chat_schemas import ChatRequest, ChatResponse, ChatStreamEvent


class IChatService(Protocol):
    async def chat(self, data: ChatRequest) -> ChatResponse | None:
        ...

    def chat_stream(self, data: ChatRequest) -> AsyncIterator[ChatStreamEvent]:
        ...
