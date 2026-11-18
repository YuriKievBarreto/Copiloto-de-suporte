from langchain_core.prompts import ChatPromptTemplate
from app.infra.llm import getLLM
from pydantic import BaseModel
from typing import Literal

Category = Literal["integracao", "cobranca", "acesso", "nenhuma"]
class QueryAnalysis(BaseModel):
    search_query: str        # pode ser igual à pergunta, se ela já estiver boa
    category: Category      # filtro, ou None se não der para inferir


ANALYZE_PROMPT = """You are the query analysis step of a helpdesk retrieval system.
The knowledge base contains manuals, FAQs and policies, searched by semantic similarity.

Given the user's question, produce:

1. search_query: the best text to search the knowledge base with.
   - Keep only what carries meaning: the problem, the system/product, error codes, names, identifiers.
   - Remove greetings, filler, and anything that does not help find a document.
   - Do NOT translate. Keep the language of the question.
   - Do NOT add facts, assumptions or terms that are not implied by the question.
   - If the question is already a good search text, return it unchanged.

2. category: the manual category the answer most likely belongs to.
   - integracao: APIs, webhooks, connecting the product to other systems.
   - cobranca: invoices, payments, charges, refunds, plans.
   - acesso: login, passwords, permissions, accounts, VPN.
   - Return "nenhuma" if the question does not clearly fit exactly one of these.
     A wrong category filter hides the right document, so when in doubt, use null.

Examples:

Question: "Oi, bom dia! Será que alguém consegue me ajudar, a minha VPN não conecta e dá erro 809?"
search_query: VPN não conecta erro 809
category: acesso

Question: "fui cobrado duas vezes na fatura desse mês, como peço estorno?"
search_query: cobrança duplicada na fatura, pedido de estorno
category: cobranca

Question: "o webhook de tickets para de disparar depois de uns minutos"
search_query: webhook de tickets para de disparar
category: integracao

Question: "Como faço para resolver isso mais rápido?"
search_query: Como faço para resolver isso mais rápido?
category: null
"""

llm = getLLM()

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", ANALYZE_PROMPT),
        ("human", "{question}")
    ]
)
