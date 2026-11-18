import pytest
from unittest.mock import MagicMock, patch
from app.agent.critic.schemas import CriticEvaluation
from tests.workflow.conftest import base_state


def _make_eval(is_grounded: bool, is_complete: bool, critique="ok", needed_action=None):
    return CriticEvaluation(
        critique=critique,
        is_grounded=is_grounded,
        is_complete=is_complete,
        needed_action=needed_action,
    )


@patch("app.agent.critic.critic_node.getLLM")
@patch("app.agent.critic.critic_node.critic_prompt")
def test_critic_aprova_quando_grounded_e_complete(mock_prompt, mock_getLLM):
    eval_result = _make_eval(is_grounded=True, is_complete=True)
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = eval_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = MagicMock()
    mock_getLLM.return_value = mock_llm
    mock_prompt.__or__ = MagicMock(return_value=chain_mock)

    from app.agent.critic.critic_node import critic_node
    state = base_state(answer="Resposta válida e embasada", question="Quantos tickets abertos?")
    result = critic_node(state)

    assert result["passed"] is True
    assert result["critic_feedback"] is None


@patch("app.agent.critic.critic_node.getLLM")
@patch("app.agent.critic.critic_node.critic_prompt")
def test_critic_reprova_quando_nao_grounded(mock_prompt, mock_getLLM):
    eval_result = _make_eval(
        is_grounded=False, is_complete=True,
        critique="Fato não embasado",
        needed_action="Buscar dados SQL",
    )
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = eval_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = MagicMock()
    mock_getLLM.return_value = mock_llm
    mock_prompt.__or__ = MagicMock(return_value=chain_mock)

    from app.agent.critic.critic_node import critic_node
    state = base_state(answer="Resposta sem suporte", question="Quantos clientes PRO?")
    result = critic_node(state)

    assert result["passed"] is False
    assert result["critic_feedback"] == "Buscar dados SQL"


@patch("app.agent.critic.critic_node.getLLM")
@patch("app.agent.critic.critic_node.critic_prompt")
def test_critic_reprova_quando_nao_complete(mock_prompt, mock_getLLM):
    eval_result = _make_eval(
        is_grounded=True, is_complete=False,
        critique="Resposta incompleta",
        needed_action=None,
    )
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = eval_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = MagicMock()
    mock_getLLM.return_value = mock_llm
    mock_prompt.__or__ = MagicMock(return_value=chain_mock)

    from app.agent.critic.critic_node import critic_node
    state = base_state(answer="Resposta parcial", question="Lista todos os tickets?")
    result = critic_node(state)

    assert result["passed"] is False
    # quando needed_action é None mas critique existe, usa critique como feedback
    assert result["critic_feedback"] == "Resposta incompleta"


@patch("app.agent.critic.critic_node.getLLM")
@patch("app.agent.critic.critic_node.critic_prompt")
def test_critic_retorna_avaliacao_serializada(mock_prompt, mock_getLLM):
    eval_result = _make_eval(is_grounded=True, is_complete=True, critique="Tudo certo")
    chain_mock = MagicMock()
    chain_mock.invoke.return_value = eval_result
    mock_llm = MagicMock()
    mock_llm.with_structured_output.return_value = MagicMock()
    mock_getLLM.return_value = mock_llm
    mock_prompt.__or__ = MagicMock(return_value=chain_mock)

    from app.agent.critic.critic_node import critic_node
    state = base_state(answer="Resposta", question="Pergunta")
    result = critic_node(state)

    assert "critic_evaluation" in result
    assert isinstance(result["critic_evaluation"], dict)
    assert "is_grounded" in result["critic_evaluation"]
