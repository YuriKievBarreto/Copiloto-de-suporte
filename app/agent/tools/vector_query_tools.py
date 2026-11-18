from langchain_core.tools import tool
from app.infra.database.vector_database import get_vector_store
from langchain_core.documents import Document
from langchain_core.tools import tool

retriever = get_vector_store().as_retriever()




@tool(parse_docstring=True)
def search_manuals(query: str) -> str:
    """Search the company's internal support manuals (knowledge base) and return the most relevant excerpts.

    The manuals contain how-to guides, configuration steps, policies and troubleshooting
    instructions (e.g. how to set up SSO, reset a password, connect to the VPN).
    Use this tool whenever the answer depends on documented procedures or rules.

    Do NOT use this tool for questions about tickets: counts, status, history, who opened
    or resolved what. Those live in the tickets database, not in the manuals.
    Do NOT use it for greetings or general-knowledge questions.

    How to write a good query:
    - Write it in Portuguese, since the manuals are in Portuguese.
    - Make it self-contained: include the key terms (product, feature, error message),
      not references like "that problem" or "the previous question".
    - If the question covers more than one topic, call the tool once per topic.
    - If the first results are not relevant, reformulate with different terms (synonyms,
      the exact error text, the feature name) and try again, at most once or twice.

    What you get back: up to a few excerpts, each with its source file and section.
    An excerpt may be incomplete (a procedure can continue in another section), so do not
    assume it is the whole manual.

    How to use the results:
    - Base your answer only on the returned excerpts and cite the source file.
    - If nothing returned answers the question, say that the manuals do not cover it.
      Never fill the gap with guesses.

    Args:
        query: Search text in Portuguese with the key terms of what is being looked up,
            e.g. "configurar SSO com Okta" or "erro de configuração SSO ACS URL".

    Returns:
        Text with the most relevant excerpts, each labeled with source file and section.
    """

    
    
    docs: list[Document] = retriever.invoke(query)
    results = format_docs(docs)
    return results
    

def format_docs(docs: list[Document]) -> str:

    if not docs:
            return "Nenhum documento relevante foi encontrado nos manuais para essa consulta."

    CAMPOS_METADATA = ("fonte", "versao", "atualizado_em")

    blocos = []
    for i, doc in enumerate(docs, start=1):
        meta = " | ".join(
            f"{k}: {doc.metadata[k]}" for k in CAMPOS_METADATA if doc.metadata.get(k)
        )
        blocos.append(f"Trecho {i} ({meta})\n{doc.page_content}")
    return "\n\n---\n\n".join(blocos)

   


