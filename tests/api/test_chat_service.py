import asyncio
import pytest
from app.services.chat_service import ChatService
from app.schemas.chat_schemas import ChatRequest, ChatResponse


class DummyAgent:
    def __init__(self, return_answer="Olá, resposta mockada"):
        self.return_answer = return_answer
        self.last_payload = None
        self.call_count = 0

    async def ainvoke(self, payload: dict) -> dict:
        self.last_payload = payload
        self.call_count += 1
        return {"answer": self.return_answer}


@pytest.fixture
def dummy_agent():
    return DummyAgent()


@pytest.fixture
def service(dummy_agent):
    return ChatService(agent=dummy_agent)


def test_chat_retorna_resposta_correta(service):
    req = ChatRequest(input="Pergunta de teste")
    response = asyncio.run(service.chat(req))
    assert isinstance(response, ChatResponse)
    assert response.answer == "Olá, resposta mockada"


def test_chat_invoca_agente_com_question_correta(service, dummy_agent):
    req = ChatRequest(input="Minha pergunta")
    asyncio.run(service.chat(req))
    assert dummy_agent.call_count == 1
    assert dummy_agent.last_payload == {"question": "Minha pergunta"}


def test_chat_repassa_resposta_do_agente_sem_alterar():
    custom_agent = DummyAgent(return_answer="Resposta customizada")
    svc = ChatService(agent=custom_agent)
    req = ChatRequest(input="Alguma pergunta")
    response = asyncio.run(svc.chat(req))
    assert response.answer == "Resposta customizada"
