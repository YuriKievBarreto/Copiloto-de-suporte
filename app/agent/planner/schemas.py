from pydantic import BaseModel, Field
from enum import StrEnum

class StepAction(StrEnum):
    SQL = "SQL"
    QDRANT = "QDRANT"
    SYNTHESIZE = "SYNTHESIZE"

class PlanStep(BaseModel):
    step_id: int = Field(description="Identificador único do passo, começa em 1")
    action: StepAction = Field(description="A ação a executar neste passo")
    description: str = Field(description="O que este passo deve recuperar ou fazer")
    depends_on : list[int] = Field(description= "IDs dos passos anteriores cujo resultado este passo precisa")


class Plan(BaseModel):
    reasoning: str = Field(description="raciocíono sobre por que o plano responda a esta pergunta")
    steps: list[PlanStep] = Field(description="Passos ordenados do plano. O ultimo deve ser SYNTHESIZE")
    out_of_scope: bool = Field(default=False, description="True se a pergunta estiver fora do escopo do HelpDesk")





