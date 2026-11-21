"""Eventos de progresso emitidos pelos nós do grafo durante o streaming.

Os helpers aqui são seguros para uso fora de um stream (ex.: ``ainvoke`` ou
testes unitários dos nós): nesses casos a emissão é simplesmente ignorada.
"""
import re
from typing import Any

from langgraph.config import get_stream_writer

NODE_LABELS = {
    "planner": "Planejando a execução",
    "executor": "Executando passo do plano",
    "synthesis_node": "Sintetizando a resposta",
    "critic": "Validando a resposta",
    "replanner": "Replanejando",
    "recusa": "Pergunta fora do escopo",
}

_SQL_PATTERN = re.compile(
    r"\b(select|insert|update|delete|with)\b.*\bfrom\b", re.IGNORECASE | re.DOTALL
)


def emit(event: str, **data: Any) -> None:
    """Envia um evento customizado ao stream; ignora se não houver stream ativo."""
    try:
        writer = get_stream_writer()
    except Exception:
        return
    writer({"event": event, **data})


def redact_sql(text: str | None) -> str | None:
    """Impede que trechos de SQL vazem para o cliente."""
    if text and _SQL_PATTERN.search(text):
        return "[detalhe omitido]"
    return text


def classify_error(error: Any) -> str:
    """Converte uma mensagem de erro em uma categoria segura para exibição."""
    if not error:
        return "unknown"
    msg = str(error).lower()
    if "timeout" in msg or "canceling statement" in msg:
        return "timeout"
    if "permission" in msg or "denied" in msg or "permiss" in msg:
        return "permission"
    if "única consulta" in msg or "somente select" in msg:
        return "invalid_query"
    if "syntax" in msg or "sintax" in msg or "does not exist" in msg or "column" in msg:
        return "syntax"
    if "documentos" in msg:
        return "no_documents"
    return "unknown"
