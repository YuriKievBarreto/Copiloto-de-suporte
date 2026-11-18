from fastapi import FastAPI
from app.routes import chat_router
from app.agent.workflow.graph import get_planner_graph

app = FastAPI()
app.include_router(chat_router.router, prefix="/chat")




if __name__ == "__main__":
    try:
        planner = get_planner_graph()
        res = planner.invoke({"question": "olá"})
        print("\nRESPOSTA:\n", res["answer"])
    except Exception as e:
        print("\n❌ ERRO DETECTADO:", e)