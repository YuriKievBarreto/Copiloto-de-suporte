import asyncio
import json

import pytest

from app.agent.planner.schemas import StepAction
from app.schemas.chat_schemas import ChatRequest, ChatStreamEvent
from app.services.chat_service import ChatService
from tests.workflow.conftest import make_plan, make_step


def start(name, **state):
    return ("tasks", {"id": name, "name": name, "input": state, "triggers": ()})


def end(name, result=None, error=None):
    return ("tasks", {"id": name, "name": name, "error": error, "result": result or {}, "interrupts": []})


def custom(event, **data):
    return ("custom", {"event": event, **data})


class FakeAgent:
    def __init__(self, chunks, raise_after=False):
        self.chunks = chunks
        self.raise_after = raise_after

    async def astream(self, payload, stream_mode=None):
        assert stream_mode == ["tasks", "custom"]
        for c in self.chunks:
            yield c
        if self.raise_after:
            raise RuntimeError("SELECT * FROM segredo falhou")


def collect(chunks, raise_after=False):
    service = ChatService(agent=FakeAgent(chunks, raise_after))

    async def run():
        return [e async for e in service.chat_stream(ChatRequest(input="pergunta"))]

    return asyncio.run(run())


def names(events):
    return [e.event for e in events]


PLAN = make_plan([make_step(1, StepAction.SQL), make_step(2, StepAction.SYNTHESIZE)])


def happy_chunks():
    return [
        start("planner"),
        end("planner", {"plan": PLAN}),
        start("executor", plan=PLAN, current_step_index=0),
        custom("step_progress", step_id=1, stage="generate_sql"),
        end("executor", {"completed_steps": [1], "failed_steps": []}),
        start("synthesis_node"),
        end("synthesis_node", {"answer": "42 tickets"}),
        start("critic"),
        end("critic", {"passed": True, "critic_feedback": None}),
    ]


def test_caminho_feliz_emite_eventos_em_ordem():
    events = collect(happy_chunks())
    assert names(events) == [
        "start", "node_start", "node_end", "node_start", "step_progress", "node_end",
        "node_start", "node_end", "node_start", "node_end", "critic", "answer", "done",
    ]
    assert events[-2].data["answer"] == "42 tickets"


def test_node_start_do_executor_informa_passo():
    events = collect(happy_chunks())
    ex = [e for e in events if e.event == "node_start" and e.data["node"] == "executor"][0]
    assert ex.data["step_id"] == 1 and ex.data["action"] == "SQL"


def test_planner_node_end_resume_plano():
    events = collect(happy_chunks())
    pl = [e for e in events if e.event == "node_end" and e.data["node"] == "planner"][0]
    assert pl.data["summary"]["steps"][0] == {"id": 1, "action": "SQL"}


def test_recusa_gera_answer():
    events = collect([start("planner"), end("planner", {"plan": PLAN}), start("recusa"),
                      end("recusa", {"answer": "fora do domínio"})])
    assert names(events)[-2:] == ["answer", "done"]


def test_replan_e_step_failed_sao_repassados():
    chunks = [
        custom("step_failed", step_id=1, error_kind="timeout"),
        custom("replan", attempt=1, origin="execution", reason="x"),
        end("synthesis_node", {"answer": "ok"}),
    ]
    events = collect(chunks)
    assert names(events)[1:3] == ["step_failed", "replan"]


def test_evento_custom_desconhecido_e_ignorado():
    events = collect([custom("qualquer_coisa"), end("synthesis_node", {"answer": "ok"})])
    assert "qualquer_coisa" not in names(events)


def test_node_error_nao_vaza_detalhes():
    events = collect([end("executor", error="SELECT * FROM tickets quebrou")])
    err = [e for e in events if e.event == "node_error"][0]
    assert "SELECT" not in err.data["message"]


def test_critic_reprovado_com_limite_emite_limit_reached():
    chunks = [
        end("replanner", {"plan": PLAN, "replan_count": 2, "critic_replan_count": 2}),
        end("synthesis_node", {"answer": "a"}),
        end("critic", {"passed": False, "critic_feedback": "faltou algo"}),
    ]
    events = collect(chunks)
    assert "limit_reached" in names(events)
    critic = [e for e in events if e.event == "critic"][0]
    assert critic.data["passed"] is False and critic.data["feedback"] == "faltou algo"


def test_critic_reprovado_sem_limite_nao_emite_limit_reached():
    chunks = [end("synthesis_node", {"answer": "a"}),
              end("critic", {"passed": False, "critic_feedback": "x"})]
    assert "limit_reached" not in names(collect(chunks))


def test_executor_com_falha_e_replans_esgotados_emite_limit_reached():
    chunks = [end("replanner", {"plan": PLAN, "replan_count": 2}),
              end("executor", {"completed_steps": [], "failed_steps": [1]}),
              end("synthesis_node", {"answer": "a"})]
    assert "limit_reached" in names(collect(chunks))


def test_feedback_do_critic_com_sql_e_redigido():
    chunks = [end("synthesis_node", {"answer": "a"}),
              end("critic", {"passed": False, "critic_feedback": "use SELECT id FROM tickets"})]
    critic = [e for e in collect(chunks) if e.event == "critic"][0]
    assert "SELECT" not in critic.data["feedback"]


def test_excecao_vira_error_e_done_sem_vazar_detalhes():
    events = collect(happy_chunks()[:2], raise_after=True)
    assert names(events)[-2:] == ["error", "done"]
    assert "segredo" not in events[-2].data["message"]


def test_sem_resposta_gera_error():
    events = collect([start("planner"), end("planner", {"plan": PLAN})])
    assert names(events)[-2:] == ["error", "done"]


def test_todos_eventos_compartilham_request_id():
    events = collect(happy_chunks())
    assert len({e.request_id for e in events}) == 1 and events[0].request_id


def test_to_sse_formato():
    e = ChatStreamEvent(event="answer", data={"answer": "olá"}, request_id="r1")
    texto = e.to_sse()
    assert texto.startswith("event: answer\ndata: ")
    assert texto.endswith("\n\n")
    payload = json.loads(texto.split("data: ", 1)[1])
    assert payload["answer"] == "olá" and payload["request_id"] == "r1" and "ts" in payload


def test_nenhum_evento_serializado_contem_sql():
    texto = "".join(e.to_sse() for e in collect(happy_chunks())).upper()
    assert "SELECT" not in texto and " FROM " not in texto
