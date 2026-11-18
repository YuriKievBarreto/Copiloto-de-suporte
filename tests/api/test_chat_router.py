import pytest


def test_post_chat_retorna_200_com_schema_correto(client):
    response = client.post("/chat/", json={"input": "Quantos tickets estão abertos?"})
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert isinstance(data["answer"], str)
    assert data["answer"] == "resposta de teste"


def test_post_chat_retorna_422_sem_input(client):
    response = client.post("/chat/", json={})
    assert response.status_code == 422


def test_post_chat_retorna_422_com_input_nulo(client):
    response = client.post("/chat/", json={"input": None})
    assert response.status_code == 422


def test_chat_service_foi_chamado_com_request_correto(client, mock_chat_service):
    client.post("/chat/", json={"input": "Qual o status do ticket 42?"})
    assert mock_chat_service.call_count == 1
    assert mock_chat_service.last_data.input == "Qual o status do ticket 42?"
