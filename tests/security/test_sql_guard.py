import pytest
from sqlmodel import SQLModel, create_engine
from app.agent.sql_agent.nodes.execute_sql import run_query
from app.db.models.agentes import Agente, Niveis
from app.db.models.clientes import Cliente, Planos
from app.db.models.tickets import Ticket, Categoria, Prioridade, StatusTicket
from sqlmodel import Session
from datetime import datetime, timezone, timedelta
from uuid import uuid4


@pytest.fixture
def security_engine(tmp_path):
    db_path = tmp_path / "security_test.db"
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def mock_agent_engine(monkeypatch, security_engine):
    monkeypatch.setattr(
        "app.agent.sql_agent.nodes.execute_sql.get_agent_engine",
        lambda: security_engine,
    )


@pytest.fixture
def seed(security_engine):
    agora = datetime.now(timezone.utc)
    cliente = Cliente(id=uuid4(), nome="Empresa X", email="x@x.com", plano=Planos.PRO, created_at=agora)
    agente = Agente(id=uuid4(), nome="Agente Z", email="z@z.com", nivel=Niveis.SENIOR, ativo=True, created_at=agora)
    ticket = Ticket(
        id=uuid4(), cliente_id=cliente.id, agente_id=agente.id,
        titulo="Bug crítico", descricao="Sistema caiu",
        status=StatusTicket.ABERTO, categoria=Categoria.INTEGRACAO,
        prioridade=Prioridade.ALTA, prazo_sla=agora + timedelta(hours=4), criado_em=agora,
    )
    with Session(security_engine) as session:
        session.add_all([cliente, agente, ticket])
        session.commit()
    return {"cliente": cliente, "agente": agente, "ticket": ticket}


# ── Consultas válidas ─────────────────────────────────────────────────────────

def test_select_simples_retorna_lista(seed):
    rows = run_query("SELECT nome FROM clientes")
    assert isinstance(rows, list)
    assert len(rows) == 1
    assert rows[0]["nome"] == "Empresa X"


def test_with_select_e_aceito(seed):
    sql = "WITH t AS (SELECT nome FROM clientes) SELECT * FROM t"
    rows = run_query(sql)
    assert isinstance(rows, list)
    assert len(rows) == 1


def test_select_contagem(seed):
    rows = run_query("SELECT COUNT(*) AS total FROM tickets")
    assert rows[0]["total"] == 1


# ── Segurança: bloqueio de DDL/DML ───────────────────────────────────────────

@pytest.mark.parametrize("sql", [
    "DELETE FROM clientes WHERE plano = 'PRO'",
    "UPDATE clientes SET plano = 'PRO' WHERE 1=1",
    "DROP TABLE clientes",
    "INSERT INTO clientes (nome) VALUES ('hack')",
])
def test_bloqueia_queries_perigosas(sql, seed):
    with pytest.raises(ValueError, match="SELECT"):
        run_query(sql)


def test_bloqueia_multiplos_statements_com_ponto_e_virgula(seed):
    # Semicolon no meio — vetor clássico de SQL injection
    with pytest.raises(ValueError):
        run_query("SELECT nome FROM clientes; DROP TABLE clientes")
