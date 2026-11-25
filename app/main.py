from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import chat_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router.router, prefix="/chat")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}





