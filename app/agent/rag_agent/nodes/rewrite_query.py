from app.agent.rag_agent.state import RAGAgentState
from app.agent.rag_agent.prompts.rewrite_prompt import rewrite_prompt
from app.infra.llm import getLLM
from pydantic import BaseModel, BeforeValidator
from typing import Literal, Annotated
llm = getLLM()


Category = Literal["integracao", "cobranca", "acesso"]

def _normalize_category(v):
    if isinstance(v, str):
        v = v.strip().lower()
        if v in {"", "null", "none", "nenhuma", "n/a"}:
            return None
    return v

OptionalCategory = Annotated[Category | None, BeforeValidator(_normalize_category)]

class RewriteResult(BaseModel):
    diagnosis: str
    search_query: str
    category: OptionalCategory = None



class QueryAnalysis(BaseModel):
    search_query: str
    category: OptionalCategory = None
    

def rewrite_query(state: RAGAgentState):
    tried = state.get("queries_tried", []) + [state["search_query"]]
    rewriter = rewrite_prompt | llm.with_structured_output(RewriteResult)
    result = rewriter.invoke({
        "question": state["question"],
        "search_query": state["search_query"],
        "category": state.get("category") or "null",
        "feedback": state["feedback"],
        "tried": "\n".join(f"- {q}" for q in tried),

    })

   

    new_query, new_category = result.search_query, result.category
    if new_query.strip().lower() in {q.strip().lower() for q in tried} and new_category == state.get("category"):
        new_category = None

    return {"search_query": new_query, "category": new_category, "queries_tried": tried}

