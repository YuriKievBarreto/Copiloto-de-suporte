from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone



class Comentario(SQLModel, table=True):
    __tablename__="comentarios"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    ticket_id: UUID = Field(foreign_key="tickets.id")
    agente_id: UUID = Field(foreign_key="agentes.id")
    conteudo: str
    interno: bool = Field(default=False)
    criado_em: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))

    ticket: "Ticket" = Relationship(
        back_populates="comentarios"
    )

    agente: "Agente" = Relationship(
        back_populates="comentarios"
    )