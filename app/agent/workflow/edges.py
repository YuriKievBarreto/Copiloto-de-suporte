from app.agent.state import AgentState


MAX_REPLANS = 2
MAX_CRITIC_REPLANS = 2

def route_after_planner(state: AgentState) -> str:
    plan = state["plan"]
    if plan.out_of_scope:
        return "recusa"
    return "executor"


def route_after_executor(state: AgentState) -> str:
    plan = state["plan"]
    idx = state["current_step_index"]

    failed_steps = state.get("failed_steps") or []
    replan_count = state.get("replan_count") or 0
    if failed_steps:
        if replan_count < MAX_REPLANS:
            return "replanner"
        else:
            return "synthesis"


    steps = plan.steps
    if idx >= len(steps):
        return "synthesis"
    next_step = steps[idx]
    if next_step.action.upper() == "SYNTHESIZE":
        return "synthesis"
    return "executor"



def route_after_replanner(state: AgentState):
    plan = state["plan"]
    if plan.out_of_scope:
        return "recusa"
    return "executor"


def route_after_critic(state: AgentState):
    passed = state.get("passed", False)
    print("PASSOU????? ", passed)
    critic_replan_count = state.get("critic_replan_count", 0)
    replan_count = state.get("replan_count", 0)

    if passed:
        return "END"
    if critic_replan_count >= MAX_CRITIC_REPLANS or replan_count >= MAX_REPLANS:
        return "END"  
    return "replanner"
