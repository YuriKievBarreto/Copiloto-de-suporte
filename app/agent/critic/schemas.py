from pydantic import BaseModel, Field
from typing import Optional

class CriticEvaluation(BaseModel):
    critique: str = Field(
        description="Diagnóstico curto (2 a 4 frases): aponte o fato específico que falhou ou explique por que a resposta está correta."
    )
    is_grounded: bool = Field(
        description="Verdadeiro apenas se todos os fatos da resposta têm suporte nas evidências."
    )
    is_complete: bool = Field(
        description="Verdadeiro apenas se a resposta cobre o que foi perguntado, ou se declara corretamente a ausência de dados."
    )
    needed_action: Optional[str] = Field(
        default=None,
        description="Somente se reprovado: instrução objetiva do que buscar ou corrigir e onde (SQL, manuais ou ambos). Nulo se aprovado.",
    )