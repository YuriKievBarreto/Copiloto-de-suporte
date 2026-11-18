import pytest
from app.agent.planner.schemas import Plan, PlanStep, StepAction
from app.agent.state import AgentState


def make_plan(steps: list[PlanStep], out_of_scope: bool = False) -> Plan:
    return Plan(
        reasoning="teste",
        steps=steps,
        out_of_scope=out_of_scope,
    )


def make_step(step_id: int, action: StepAction, depends_on=None) -> PlanStep:
    return PlanStep(
        step_id=step_id,
        action=action,
        description="passo de teste",
        depends_on=depends_on or [],
    )


def base_state(**overrides) -> AgentState:
    defaults: dict = {
        "question": "Pergunta de teste",
        "plan": None,
        "current_step_index": 0,
        "completed_steps": [],
        "observations": {},
        "sql_evidence": None,
        "rag_evidence": None,
        "replan_count": 0,
        "errors": {},
        "failed_steps": [],
        "answer": "",
        "critic_evaluation": None,
        "critic_feedback": None,
        "critic_replan_count": 0,
        "passed": False,
    }
    return {**defaults, **overrides}
