from fastapi import APIRouter, Depends
from app.dependencies import get_chat_service
from app.services.chat_service import ChatService
from app.schemas.chat_schemas import ChatRequest, ChatResponse



router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(req: ChatRequest, chat_service : ChatService = Depends(get_chat_service)) -> ChatResponse:
    return await chat_service.chat(req)
