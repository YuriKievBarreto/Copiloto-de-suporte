import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import get_chat_service, get_compiled_planner_graph
from app.schemas.chat_schemas import ChatRequest, ChatResponse
from unittest.mock import MagicMock


class FakeChatService:
    def __init__(self):
        self.last_data = None
        self.call_count = 0

    async def chat(self, data: ChatRequest) -> ChatResponse:
        self.last_data = data
        self.call_count += 1
        return ChatResponse(answer="resposta de teste")


@pytest.fixture
def mock_chat_service():
    """Serviço fake concreto determinístico."""
    return FakeChatService()


@pytest.fixture
def client(mock_chat_service):
    """TestClient com override da dependência."""
    app.dependency_overrides[get_chat_service] = lambda: mock_chat_service
    app.dependency_overrides[get_compiled_planner_graph] = lambda: MagicMock()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
