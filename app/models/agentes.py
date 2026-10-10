from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone
from enum import StrEnum

class Niveis(StrEnum):
    TRAINEE = "trainee"
    JUNIOR = "junior"
    PLENO = "pleno"
    SENIOR = "senior"


class Agente(SQLModel, table=True):
    __tablename__="agentes"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nome: str
    email: str
    nivel: Niveis
    ativo: bool = Field(default=True)
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))

    tickets: list["Ticket"] = Relationship(
        back_populates="agente"
    )

    comentarios: list["Comentario"] = Relationship(
        back_populates="agente"
    )