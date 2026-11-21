import json
from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    input: str


class ChatResponse(BaseModel):
    answer: str


StreamEventName = Literal[
    "start",
    "node_start",
    "node_end",
    "node_error",
    "step_progress",
    "step_failed",
    "replan",
    "critic",
    "limit_reached",
    "answer",
    "error",
    "done",
]


class ChatStreamEvent(BaseModel):
    event: StreamEventName
    data: dict[str, Any] = Field(default_factory=dict)
    request_id: str = ""
    ts: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_sse(self) -> str:
        payload = {**self.data, "request_id": self.request_id, "ts": self.ts}
        return f"event: {self.event}\ndata: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"
