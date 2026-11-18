import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.db import models
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from sqlmodel import SQLModel, Session, create_engine
from sqlalchemy.pool import StaticPool

from app.db.models.agentes import Agente, Niveis
from app.db.models.clientes import Cliente, Planos
from app.db.models.tickets import Ticket, Categoria, Prioridade, StatusTicket

@pytest.fixture
def test_engine(tmp_path):
    db_path = tmp_path / "test_db"

    engine = create_engine(
        f"sqlite:///{db_path}"
    )

    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def mock_agent_engine(monkeypatch, test_engine):
    monkeypatch.setattr("app.agent.tools.sql_tools.get_agent_engine", lambda: test_engine)

@pytest.fixture
def seed_data(test_engine):
    """
    Popula o banco com um conjunto mínimo e determinístico de dados de teste.
    """
    agora = datetime.now(timezone.utc)

    # 1. Clientes controlados
    cliente_pro = Cliente(
        id=uuid4(),
        nome="Tech Corp",
        email="contato@techcorp.com",
        plano=Planos.PRO,
        created_at=agora,
    )
    cliente_free = Cliente(
        id=uuid4(),
        nome="Startup Soft",
        email="admin@startupserver.com",
        plano=Planos.FREE,
        created_at=agora,
    )

    # 2. Agente
    agente = Agente(
        id=uuid4(),
        nome="Agente Ana",
        email="ana@helpdesk.interno",
        nivel=Niveis.SENIOR,
        ativo=True,
        created_at=agora,
    )

    # 3. Tickets com status conhecidos
    ticket_aberto = Ticket(
        id=uuid4(),
        cliente_id=cliente_pro.id,
        agente_id=agente.id,
        titulo="Erro 504 no ERP",
        descricao="Timeout ao integrar com ERP",
        status=StatusTicket.ABERTO,
        categoria=Categoria.INTEGRACAO,
        prioridade=Prioridade.ALTA,
        prazo_sla=agora + timedelta(hours=12),
        criado_em=agora,
    )
    ticket_fechado = Ticket(
        id=uuid4(),
        cliente_id=cliente_free.id,
        agente_id=agente.id,
        titulo="Dúvida Boleto",
        descricao="Boleto não chegou",
        status=StatusTicket.FECHADO,
        categoria=Categoria.COBRANCA,
        prioridade=Prioridade.BAIXA,
        prazo_sla=agora + timedelta(hours=72),
        criado_em=agora - timedelta(days=2),
        resolvido_em=agora - timedelta(days=1),
    )

    with Session(test_engine) as session:
        session.add_all([cliente_pro, cliente_free, agente, ticket_aberto, ticket_fechado])
        session.commit()

    return {
        "clientes": [cliente_pro, cliente_free],
        "agente": agente,
        "tickets": [ticket_aberto, ticket_fechado],
    }

