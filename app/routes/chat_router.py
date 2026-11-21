from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from app.dependencies import get_chat_service
from app.services.interfaces.chat_service_interface import IChatService
from app.schemas.chat_schemas import ChatRequest, ChatResponse


router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    chat_service: IChatService = Depends(get_chat_service),
) -> ChatResponse:
    return await chat_service.chat(req)


@router.post("/stream")
async def chat_stream(
    req: ChatRequest,
    chat_service: IChatService = Depends(get_chat_service),
) -> StreamingResponse:
    async def event_generator():
        async for event in chat_service.chat_stream(req):
            yield event.to_sse()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
