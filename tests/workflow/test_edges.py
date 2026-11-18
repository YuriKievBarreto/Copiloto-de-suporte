import pytest
from app.agent.workflow.edges import (
    route_after_planner,
    route_after_executor,
    route_after_replanner,
    route_after_critic,
    MAX_REPLANS,
    MAX_CRITIC_REPLANS,
)
from app.agent.planner.schemas import StepAction
from tests.workflow.conftest import base_state, make_plan, make_step


# ── route_after_planner ───────────────────────────────────────────────────────

class TestRouteAfterPlanner:
    def test_roteia_para_executor_quando_in_scope(self):
        plan = make_plan([make_step(1, StepAction.SQL)])
        state = base_state(plan=plan)
        assert route_after_planner(state) == "executor"

    def test_roteia_para_recusa_quando_out_of_scope(self):
        plan = make_plan([], out_of_scope=True)
        state = base_state(plan=plan)
        assert route_after_planner(state) == "recusa"


# ── route_after_executor ──────────────────────────────────────────────────────

class TestRouteAfterExecutor:
    def test_vai_para_replanner_se_ha_falha_e_replan_abaixo_do_limite(self):
        plan = make_plan([make_step(1, StepAction.SQL)])
        state = base_state(plan=plan, failed_steps=[1], replan_count=0)
        assert route_after_executor(state) == "replanner"

    def test_vai_para_synthesis_se_falha_mas_atingiu_max_replans(self):
        plan = make_plan([make_step(1, StepAction.SQL)])
        state = base_state(plan=plan, failed_steps=[1], replan_count=MAX_REPLANS)
        assert route_after_executor(state) == "synthesis"

    def test_vai_para_synthesis_quando_indice_ultrapassa_steps(self):
        plan = make_plan([make_step(1, StepAction.SQL)])
        # current_step_index=1 significa que o único passo já foi processado
        state = base_state(plan=plan, current_step_index=1)
        assert route_after_executor(state) == "synthesis"

    def test_continua_no_executor_enquanto_houver_steps_pendentes(self):
        plan = make_plan([
            make_step(1, StepAction.SQL),
            make_step(2, StepAction.QDRANT),
        ])
        state = base_state(plan=plan, current_step_index=1)
        assert route_after_executor(state) == "executor"

    def test_vai_para_synthesis_quando_proximo_step_e_synthesize(self):
        plan = make_plan([
            make_step(1, StepAction.SQL),
            make_step(2, StepAction.SYNTHESIZE),
        ])
        state = base_state(plan=plan, current_step_index=1)
        assert route_after_executor(state) == "synthesis"


# ── route_after_replanner ─────────────────────────────────────────────────────

class TestRouteAfterReplanner:
    def test_vai_para_executor_quando_in_scope(self):
        plan = make_plan([make_step(1, StepAction.SQL)])
        state = base_state(plan=plan)
        assert route_after_replanner(state) == "executor"

    def test_vai_para_recusa_quando_out_of_scope(self):
        plan = make_plan([], out_of_scope=True)
        state = base_state(plan=plan)
        assert route_after_replanner(state) == "recusa"


# ── route_after_critic ────────────────────────────────────────────────────────

class TestRouteAfterCritic:
    def test_finaliza_quando_passou(self):
        state = base_state(passed=True)
        assert route_after_critic(state) == "END"

    def test_finaliza_quando_critic_replan_atingiu_limite(self):
        state = base_state(passed=False, critic_replan_count=MAX_CRITIC_REPLANS, replan_count=0)
        assert route_after_critic(state) == "END"

    def test_finaliza_quando_replan_geral_atingiu_limite(self):
        state = base_state(passed=False, critic_replan_count=0, replan_count=MAX_REPLANS)
        assert route_after_critic(state) == "END"

    def test_vai_para_replanner_quando_reprovado_e_dentro_do_limite(self):
        state = base_state(passed=False, critic_replan_count=0, replan_count=0)
        assert route_after_critic(state) == "replanner"
