from app.agent.rag_agent.state import RAGAgentState
from app.agent.rag_agent.prompts.analyze_query import prompt, QueryAnalysis
from app.infra.llm import getLLM

llm = getLLM()

def analyze_query(state: RAGAgentState):
    queries_tried = state["queries_tried"]
    analyzer = prompt | llm.with_structured_output(QueryAnalysis)
    
    result = analyzer.invoke({"question": state["question"]})
    category = None if result.category == "nenhuma" else result.category

    queries_tried.append(result.search_query)
    return {"search_query":result.search_query, "category": category, "queries_tried": queries_tried}




