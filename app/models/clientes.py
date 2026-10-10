from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone
from enum import StrEnum

class Planos(StrEnum):
    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"


class Cliente(SQLModel, table=True):
    __tablename__="clientes"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    nome: str
    email: str
    plano: Planos
    created_at: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))

    tickets: list["Ticket"] = Relationship(
        back_populates="cliente"
    )