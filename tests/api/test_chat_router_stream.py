from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_chat_service, get_compiled_planner_graph
from app.main import app
from app.schemas.chat_schemas import ChatStreamEvent


class FakeStreamService:
    async def chat(self, data):
        raise NotImplementedError

    async def chat_stream(self, data):
        yield ChatStreamEvent(event="start", data={}, request_id="r")
        yield ChatStreamEvent(event="answer", data={"answer": data.input}, request_id="r")
        yield ChatStreamEvent(event="done", data={}, request_id="r")


@pytest.fixture
def stream_client():
    app.dependency_overrides[get_chat_service] = lambda: FakeStreamService()
    app.dependency_overrides[get_compiled_planner_graph] = lambda: MagicMock()
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def test_stream_retorna_event_stream(stream_client):
    r = stream_client.post("/chat/stream", json={"input": "oi"})
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/event-stream")
    assert r.headers["cache-control"] == "no-cache"


def test_stream_corpo_em_formato_sse(stream_client):
    body = stream_client.post("/chat/stream", json={"input": "oi"}).text
    blocos = [b for b in body.split("\n\n") if b]
    assert [b.split("\n")[0] for b in blocos] == ["event: start", "event: answer", "event: done"]
    assert '"answer": "oi"' in body


def test_stream_payload_invalido_422(stream_client):
    assert stream_client.post("/chat/stream", json={}).status_code == 422
