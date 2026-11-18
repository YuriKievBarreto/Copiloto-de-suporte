from app.agent.rag_agent.graph import route_after_grade
from app.agent.rag_agent.state import MAX_ATTEMPTS, Status


def _rag_state(is_relevant: bool, attempts: int = 0):
    return {
        "question": "teste",
        "search_query": "",
        "queries_tried": [],
        "feedback": "",
        "documents": [],
        "is_relevant": is_relevant,
        "attempts": attempts,
        "status": Status.RUNNING,
    }


def test_relevante_vai_para_success():
    assert route_after_grade(_rag_state(is_relevant=True)) == "success"


def test_irrelevante_abaixo_do_limite_reescreve():
    assert route_after_grade(_rag_state(is_relevant=False, attempts=1)) == "rewrite"


def test_irrelevante_exatamente_no_limite_vai_para_failed():
    assert route_after_grade(_rag_state(is_relevant=False, attempts=MAX_ATTEMPTS)) == "failed"


def test_relevante_ignora_numero_de_tentativas():
    # Mesmo com várias tentativas, se for relevante, sempre vai para success
    assert route_after_grade(_rag_state(is_relevant=True, attempts=MAX_ATTEMPTS)) == "success"
