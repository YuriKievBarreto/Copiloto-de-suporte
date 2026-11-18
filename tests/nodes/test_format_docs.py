import pytest
from langchain_core.documents import Document
from app.agent.tools.vector_query_tools import format_docs


def test_format_docs_vazio_retorna_mensagem_de_fallback():
    resultado = format_docs([])
    assert "Nenhum documento relevante" in resultado


def test_format_docs_inclui_conteudo_do_documento():
    doc = Document(
        page_content="Conteúdo do manual SSO",
        metadata={"fonte": "manual_sso.pdf", "versao": "1.2", "atualizado_em": "2024-01"},
    )
    resultado = format_docs([doc])
    assert "Conteúdo do manual SSO" in resultado


def test_format_docs_inclui_metadados_de_fonte():
    doc = Document(
        page_content="Texto qualquer",
        metadata={"fonte": "manual_vpn.pdf", "versao": "2.0", "atualizado_em": "2024-06"},
    )
    resultado = format_docs([doc])
    assert "manual_vpn.pdf" in resultado
    assert "2.0" in resultado


def test_format_docs_sem_metadados_opcionais_nao_quebra():
    doc = Document(page_content="Texto simples", metadata={})
    resultado = format_docs([doc])
    assert "Texto simples" in resultado


def test_format_docs_multiplos_documentos_separados_por_delimitador():
    docs = [
        Document(page_content="Doc 1", metadata={"fonte": "a.pdf"}),
        Document(page_content="Doc 2", metadata={"fonte": "b.pdf"}),
    ]
    resultado = format_docs(docs)
    assert "Doc 1" in resultado
    assert "Doc 2" in resultado
    assert "---" in resultado


def test_format_docs_numera_trechos_sequencialmente():
    docs = [
        Document(page_content="Primeiro", metadata={}),
        Document(page_content="Segundo", metadata={}),
        Document(page_content="Terceiro", metadata={}),
    ]
    resultado = format_docs(docs)
    assert "Trecho 1" in resultado
    assert "Trecho 2" in resultado
    assert "Trecho 3" in resultado
