from app.agent.sql_agent.graph import route
from app.agent.sql_agent.state import MAX_ATTEMPTS


def _sql_state(error=None, attempts=0):
    return {
        "question": "teste",
        "sql": "SELECT 1",
        "result": None,
        "error": error,
        "attempts": attempts,
    }


def test_sem_erro_vai_para_fim():
    assert route(_sql_state(error=None)) == "fim"


def test_com_erro_abaixo_do_limite_tenta_de_novo():
    assert route(_sql_state(error="syntax error", attempts=1)) == "tentar_de_novo"


def test_com_erro_exatamente_no_limite_vai_para_fim():
    assert route(_sql_state(error="timeout", attempts=MAX_ATTEMPTS)) == "fim"


def test_sem_erro_independente_de_attempts():
    # Sem erro, sempre vai para fim independentemente do número de tentativas
    assert route(_sql_state(error=None, attempts=MAX_ATTEMPTS + 5)) == "fim"
