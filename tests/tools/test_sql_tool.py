import json
import pytest
from app.agent.tools.sql_tools import execute_sql, get_schema


# ── Consultas válidas ──────────────────────────────────────────────────────────

def test_executa_sql_com_sucesso(seed_data):
    resultado = execute_sql.invoke({"sql": "SELECT nome, plano FROM clientes WHERE plano = 'PRO'"})
    rows = json.loads(resultado)
    assert len(rows) == 1
    assert rows[0]["nome"] == "Tech Corp"
    assert rows[0]["plano"] == "PRO"


def test_executa_sql_contagem_tickets(seed_data):
    resultado = execute_sql.invoke({"sql": "SELECT COUNT(*) as total FROM tickets"})
    rows = json.loads(resultado)
    assert rows[0]["total"] == 2


# ── Bloqueio de queries perigosas ─────────────────────────────────────────────

def test_proibe_sql_diferente_de_select_delete(seed_data):
    resultado = execute_sql.invoke({"sql": "DELETE FROM clientes WHERE plano = 'PRO'"})
    assert resultado.startswith("Erro")


def test_proibe_sql_drop_table(seed_data):
    resultado = execute_sql.invoke({"sql": "DROP TABLE tickets"})
    assert resultado.startswith("Erro")


# ── Consulta malformada retorna mensagem de erro ──────────────────────────────

def test_consulta_malformada_devolve_erro_como_texto(seed_data):
    resultado = execute_sql.invoke({"sql": "SELECT id FOM tickets"})
    assert resultado.startswith("Erro SQL:")


# ── Schema ────────────────────────────────────────────────────────────────────

def test_get_schema_retorna_tabelas(seed_data):
    schema = get_schema.invoke({})
    assert "Table: clientes" in schema
    assert "Table: tickets" in schema
