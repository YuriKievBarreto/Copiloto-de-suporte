import logging
import uuid
from typing import Any, AsyncIterator

from langgraph.graph.state import CompiledStateGraph

from app.agent.events import NODE_LABELS, redact_sql
from app.agent.workflow.edges import MAX_CRITIC_REPLANS, MAX_REPLANS
from app.schemas.chat_schemas import ChatRequest, ChatResponse, ChatStreamEvent
from app.services.interfaces.chat_service_interface import IChatService

logger = logging.getLogger(__name__)

CUSTOM_EVENTS = {"step_progress", "step_failed", "replan"}


def _summarize(node: str, result: dict[str, Any]) -> dict[str, Any]:
    """Resumo pequeno e seguro (sem SQL nem linhas de dados) do resultado de um nó."""
    if node == "planner" or node == "replanner":
        plan = result.get("plan")
        steps = [
            {"id": s.step_id, "action": str(s.action)} for s in getattr(plan, "steps", [])
        ]
        return {"steps": steps, "out_of_scope": bool(getattr(plan, "out_of_scope", False))}
    if node == "executor":
        return {
            "completed_steps": result.get("completed_steps", []),
            "failed_steps": result.get("failed_steps", []),
        }
    if node == "critic":
        return {"passed": bool(result.get("passed"))}
    return {}


class ChatService(IChatService):
    def __init__(self, agent: CompiledStateGraph) -> None:
        self.agent = agent

    async def chat(self, data: ChatRequest) -> ChatResponse:
        res = await self.agent.ainvoke({"question": data.input})
        return ChatResponse(answer=res["answer"])

    async def chat_stream(self, data: ChatRequest) -> AsyncIterator[ChatStreamEvent]:
        request_id = uuid.uuid4().hex

        def ev(event: str, **payload: Any) -> ChatStreamEvent:
            return ChatStreamEvent(event=event, data=payload, request_id=request_id)

        yield ev("start", question_length=len(data.input))
        answer: str | None = None
        replan_count = 0
        critic_replan_count = 0

        try:
            async for mode, chunk in self.agent.astream(
                {"question": data.input}, stream_mode=["tasks", "custom"]
            ):
                if mode == "custom":
                    name = chunk.get("event") if isinstance(chunk, dict) else None
                    if name in CUSTOM_EVENTS:
                        payload = {k: v for k, v in chunk.items() if k != "event"}
                        yield ev(name, **payload)
                    continue

                node = chunk["name"]
                label = NODE_LABELS.get(node, node)

                if "input" in chunk:  # início do nó
                    extra: dict[str, Any] = {}
                    if node == "executor":
                        try:
                            state = chunk["input"]
                            step = state["plan"].steps[state["current_step_index"]]
                            extra = {"step_id": step.step_id, "action": str(step.action)}
                        except Exception:
                            extra = {}
                    yield ev("node_start", node=node, label=label, **extra)
                    continue

                if chunk.get("error"):
                    yield ev("node_error", node=node, message="Falha ao executar a etapa")
                    continue

                result = chunk.get("result") or {}
                yield ev("node_end", node=node, label=label, summary=_summarize(node, result))

                if "answer" in result and node in ("synthesis_node", "recusa"):
                    answer = result["answer"]

                if node == "replanner":
                    replan_count = result.get("replan_count", replan_count)
                    critic_replan_count = result.get("critic_replan_count", critic_replan_count)

                elif node == "executor":
                    if result.get("failed_steps") and replan_count >= MAX_REPLANS:
                        yield ev(
                            "limit_reached",
                            kind="replan",
                            message="Limite de replanejamentos atingido; seguindo com o que foi obtido.",
                        )

                elif node == "critic":
                    passed = bool(result.get("passed"))
                    yield ev(
                        "critic",
                        passed=passed,
                        feedback=redact_sql(result.get("critic_feedback")),
                    )
                    if not passed and (
                        critic_replan_count >= MAX_CRITIC_REPLANS or replan_count >= MAX_REPLANS
                    ):
                        yield ev(
                            "limit_reached",
                            kind="critic_replan",
                            message="Limite de revisões atingido; resposta entregue sem aprovação do critic.",
                        )

            if answer is None:
                yield ev("error", message="O workflow terminou sem gerar resposta.")
            else:
                yield ev("answer", answer=answer)
        except Exception:
            logger.exception("Falha no streaming do workflow")
            yield ev("error", message="Erro interno ao processar a solicitação.")
        finally:
            yield ev("done")
