from app.agent.events import classify_error, emit, redact_sql


def test_emit_fora_de_stream_nao_lanca_excecao():
    emit("step_progress", step_id=1)


def test_classify_error_categorias():
    assert classify_error("canceling statement due to statement timeout") == "timeout"
    assert classify_error("permission denied for table x") == "permission"
    assert classify_error("Envie uma única consulta SELECT") == "invalid_query"
    assert classify_error('column "foo" does not exist') == "syntax"
    assert classify_error("não foi possível recuperar documentos relevantes") == "no_documents"
    assert classify_error(None) == "unknown"
    assert classify_error("algo estranho") == "unknown"


def test_redact_sql_oculta_consultas():
    assert redact_sql("rode SELECT * FROM tickets") == "[detalhe omitido]"
    assert redact_sql("refaça o plano usando manuais") == "refaça o plano usando manuais"
    assert redact_sql(None) is None
