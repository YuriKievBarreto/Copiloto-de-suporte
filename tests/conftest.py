"""
conftest.py global — bloqueia TODA conexão de rede e modelos pesados durante os testes.

Estratégia: usar sys.modules para substituir módulos problemáticos ANTES que qualquer
módulo do projeto os importe. Isso impede que LangGraph, nodes de RAG/SQL e demais
módulos tentem conectar a Qdrant, AWS Bedrock ou carregar modelos HuggingFace.
"""
import sys
import os
from unittest.mock import MagicMock, patch

# Desabilita tracing do LangSmith/LangChain
os.environ["LANGCHAIN_TRACING_V2"] = "false"
os.environ["LANGSMITH_TRACING"] = "false"

# ── 1. Bloqueia HuggingFaceEmbeddings ────────────────────────────────────────
_mock_embeddings = MagicMock()
_mock_hf = MagicMock()
_mock_hf.HuggingFaceEmbeddings = MagicMock(return_value=_mock_embeddings)
sys.modules.setdefault("langchain_huggingface", _mock_hf)

# ── 2. Bloqueia botocore / boto3 / langchain_aws ─────────────────────────────
sys.modules.setdefault("botocore", MagicMock())
sys.modules.setdefault("botocore.config", MagicMock())
sys.modules.setdefault("boto3", MagicMock())
_mock_aws = MagicMock()
_mock_aws.ChatBedrockConverse = MagicMock(return_value=MagicMock())
sys.modules.setdefault("langchain_aws", _mock_aws)

# ── 3. Bloqueia getLLM globalmente ──────────────────────────────────────────
_mock_llm = MagicMock()
_mock_llm_module = MagicMock()
_mock_llm_module.getLLM = MagicMock(return_value=_mock_llm)
sys.modules.setdefault("app.infra.llm", _mock_llm_module)

# ── 4. Bloqueia get_vector_store antes do retrieve_node importá-la ────────────
_mock_vector_store = MagicMock()
_mock_retriever = MagicMock()
_mock_retriever.invoke.return_value = []
_mock_vector_store.as_retriever.return_value = _mock_retriever
_mock_vector_store.similarity_search.return_value = []

_mock_vector_db_module = MagicMock()
_mock_vector_db_module.get_vector_store = MagicMock(return_value=_mock_vector_store)
sys.modules.setdefault("app.infra.database.vector_database", _mock_vector_db_module)

# ─────────────────────────────────────────────────────────────────────────────
# Fixtures do banco de dados (compartilhadas entre tools, security, nodes)
# ─────────────────────────────────────────────────────────────────────────────
import pytest
from sqlmodel import SQLModel, Session, create_engine
from app.db import models
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from app.db.models.agentes import Agente, Niveis
from app.db.models.clientes import Cliente, Planos
from app.db.models.tickets import Ticket, Categoria, Prioridade, StatusTicket


@pytest.fixture
def test_engine(tmp_path):
    db_path = tmp_path / "test_db.sqlite"
    engine = create_engine(f"sqlite:///{db_path}")
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(autouse=True)
def mock_agent_engine(monkeypatch, test_engine):
    monkeypatch.setattr("app.agent.tools.sql_tools.get_agent_engine", lambda: test_engine)


@pytest.fixture
def seed_data(test_engine):
    """Popula o banco com um conjunto mínimo e determinístico de dados de teste."""
    agora = datetime.now(timezone.utc)

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
    agente = Agente(
        id=uuid4(),
        nome="Agente Ana",
        email="ana@helpdesk.interno",
        nivel=Niveis.SENIOR,
        ativo=True,
        created_at=agora,
    )
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
