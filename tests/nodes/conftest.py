import pytest
from unittest.mock import patch, MagicMock


@pytest.fixture(autouse=True)
def block_llm_calls():
    """Impede chamadas reais ao LLM em todos os testes deste pacote."""
    with patch("app.infra.llm.getLLM") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture(autouse=True)
def block_vector_store():
    """Impede conexão com Qdrant ao importar vector_query_tools."""
    mock_retriever = MagicMock()
    mock_retriever.invoke.return_value = []
    with patch("app.infra.database.vector_database.get_vector_store") as mock_vs:
        mock_vs.return_value.as_retriever.return_value = mock_retriever
        yield mock_retriever
