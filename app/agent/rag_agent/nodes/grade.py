from app.agent.rag_agent.state import RAGAgentState
from pydantic import BaseModel
from app.agent.rag_agent.prompts.grade import grade_prompt
from app.agent.llm import getLLM

llm = getLLM()

class GradeResult(BaseModel):
    feedback: str
    is_relevant: bool

def grade(state: RAGAgentState) -> dict:
    grader =  grade_prompt | llm.with_structured_output(GradeResult)

    docs = state["documents"]
    if not docs:
        return {"is_relevant": False, "feedback": "No chunks were retrieved."}

    result = grader.invoke({
        "question": state["question"],
        "documents": format_docs(docs),
    })
    return {"is_relevant": result.is_relevant, "feedback": result.feedback}



def format_docs(docs) -> str:
    return "\n\n".join(
        f"[{i}] ({d.metadata.get('categoria')}) {d.metadata.get('titulo')}\n{d.page_content}"
        for i, d in enumerate(docs, start=1)
    )