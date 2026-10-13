from app.agent.tools.sql_tools import execute_sql, get_schema
import pytest
from sqlalchemy.exc import OperationalError
# executa sql normalemente
# proíbe ações diferentes de SELECT

def test_executa_sql_com_sucesso(seed_data):
    resultado = execute_sql.invoke({"sql": "SELECT nome, plano FROM clientes WHERE plano = 'PRO';"})

    assert len(resultado) == 1
    assert resultado[0]["nome"] == "Tech Corp"
    assert resultado[0]["plano"] == "PRO"


def test_executa_sql_contagem_tickets(seed_data):
        resultado = execute_sql.invoke({"sql": "SELECT COUNT(*) as total FROM tickets;"})
        
        assert resultado[0]["total"] == 2

def test_proibe_sql_diferente_de_select(seed_data):
    with pytest.raises(ValueError) as exc_info:
        execute_sql.invoke({"sql": "DELETE nome, plano FROM clientes WHERE plano = 'PRO';"})

    assert "Only SELECT queries are allowed." in str(exc_info.value)

    with pytest.raises(ValueError, match="Only SELECT queries are allowed"):
        execute_sql.invoke({"sql": "DROP TABLE tickets;"})


def test_get_schema_retorna_tabelas(seed_data):
        schema = get_schema.invoke({})
        
        assert "Table: clientes" in schema
        assert "Table: tickets" in schema


def test_consulta_malformada_devolve_erro_como_texto(seed_data):
    with pytest.raises(OperationalError) as exc_info:
        execute_sql.invoke({"sql": "SELECT id FOM tickets"})

    assert "syntax error" in str(exc_info.value)
    