import pytest
from unittest.mock import MagicMock, patch
from app.agent.planner.nodes.executor_node import _build_context, executor
from app.agent.planner.schemas import StepAction
from app.agent.rag_agent.state import Status as RagStatus
from tests.workflow.conftest import base_state, make_plan, make_step


# ── _build_context (função pura) ─────────────────────────────────────────────

def test_build_context_sem_dependencias_retorna_vazio():
    step = make_step(1, StepAction.SQL, depends_on=[])
    resultado = _build_context(step, observations={})
    assert resultado == ""


def test_build_context_com_dependencias_inclui_resultado():
    step = make_step(2, StepAction.QDRANT, depends_on=[1])
    observations = {1: {"rows": [{"id": 1, "status": "ABERTO"}]}}
    resultado = _build_context(step, observations)
    assert "passo 1" in resultado
    assert str(observations[1]) in resultado


def test_build_context_ignora_dependencias_sem_observacao():
    step = make_step(2, StepAction.QDRANT, depends_on=[1])
    resultado = _build_context(step, observations={})
    assert resultado == ""


def test_build_context_concatena_multiplas_dependencias():
    step = make_step(3, StepAction.QDRANT, depends_on=[1, 2])
    observations = {
        1: {"rows": [{"id": 1}]},
        2: {"documents": ["doc A"]},
    }
    resultado = _build_context(step, observations)
    assert "passo 1" in resultado
    assert "passo 2" in resultado


# ── executor com step SQL ────────────────────────────────────────────────────

@patch("app.agent.planner.nodes.executor_node.sql_graph")
def test_executor_registra_step_em_completed_quando_sql_sucesso(mock_sql_graph):
    mock_sql_graph.invoke.return_value = {
        "result": [{"id": 1}], "error": None, "sql": "SELECT 1"
    }
    plan = make_plan([make_step(1, StepAction.SQL)])
    state = base_state(plan=plan, current_step_index=0)
    result = executor(state)
    assert 1 in result["completed_steps"]
    assert 1 not in result["failed_steps"]


@patch("app.agent.planner.nodes.executor_node.sql_graph")
def test_executor_registra_step_em_failed_quando_sql_falha(mock_sql_graph):
    mock_sql_graph.invoke.return_value = {
        "result": None, "error": "timeout na conexão", "sql": None
    }
    plan = make_plan([make_step(1, StepAction.SQL)])
    state = base_state(plan=plan, current_step_index=0)
    result = executor(state)
    assert 1 in result["failed_steps"]
    assert "timeout" in result["errors"][1]


@patch("app.agent.planner.nodes.executor_node.sql_graph")
def test_executor_incrementa_indice_do_passo(mock_sql_graph):
    mock_sql_graph.invoke.return_value = {
        "result": [{"id": 1}], "error": None, "sql": "SELECT 1"
    }
    plan = make_plan([make_step(1, StepAction.SQL)])
    state = base_state(plan=plan, current_step_index=0)
    result = executor(state)
    assert result["current_step_index"] == 1


@patch("app.agent.planner.nodes.executor_node.sql_graph")
def test_executor_armazena_sql_evidence(mock_sql_graph):
    mock_sql_graph.invoke.return_value = {
        "result": [{"total": 42}], "error": None, "sql": "SELECT COUNT(*) FROM tickets"
    }
    plan = make_plan([make_step(1, StepAction.SQL)])
    state = base_state(plan=plan, current_step_index=0)
    result = executor(state)
    assert result["sql_evidence"] is not None
    assert result["sql_evidence"]["status"] == "success"


# ── executor com step QDRANT ─────────────────────────────────────────────────

@patch("app.agent.planner.nodes.executor_node.rag_graph")
def test_executor_armazena_rag_evidence_quando_sucesso(mock_rag_graph):
    mock_rag_graph.invoke.return_value = {
        "status": RagStatus.SUCCESS,
        "documents": [{"content": "Manual de SSO"}],
    }
    plan = make_plan([make_step(1, StepAction.QDRANT)])
    state = base_state(plan=plan, current_step_index=0)
    result = executor(state)
    assert result["rag_evidence"] is not None
    assert result["rag_evidence"]["status"] == "success"
    assert 1 in result["completed_steps"]


@patch("app.agent.planner.nodes.executor_node.rag_graph")
def test_executor_registra_rag_como_failed_quando_status_errado(mock_rag_graph):
    mock_rag_graph.invoke.return_value = {
        "status": RagStatus.FAILED,
        "documents": [],
    }
    plan = make_plan([make_step(1, StepAction.QDRANT)])
    state = base_state(plan=plan, current_step_index=0)
    result = executor(state)
    assert 1 in result["failed_steps"]


# ── executor com índice além dos steps ──────────────────────────────────────

def test_executor_retorna_dict_vazio_se_indice_fora_dos_steps():
    plan = make_plan([make_step(1, StepAction.SQL)])
    state = base_state(plan=plan, current_step_index=5)
    result = executor(state)
    assert result == {}
