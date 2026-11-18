import pytest
from app.agent.tools.sql_tools import get_schema


@pytest.fixture(autouse=True)
def mock_agent_engine(monkeypatch, test_engine):
    """Redireciona o engine do get_schema para SQLite in-memory do conftest global."""
    monkeypatch.setattr("app.agent.tools.sql_tools.get_agent_engine", lambda: test_engine)


def test_get_schema_contem_tabelas_principais(seed_data):
    schema = get_schema.invoke({})
    assert "Table: clientes" in schema
    assert "Table: tickets" in schema
    assert "Table: agentes" in schema


def test_get_schema_contem_colunas(seed_data):
    schema = get_schema.invoke({})
    assert "nome" in schema
    assert "email" in schema
    assert "status" in schema


def test_get_schema_contem_chaves_estrangeiras(seed_data):
    schema = get_schema.invoke({})
    assert "FK:" in schema


def test_get_schema_e_string(seed_data):
    schema = get_schema.invoke({})
    assert isinstance(schema, str)
    assert len(schema) > 0
