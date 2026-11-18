from sqlmodel import SQLModel, Field, Relationship
from uuid import uuid4, UUID
from datetime import datetime, timezone
from enum import StrEnum

class StatusTicket(StrEnum):
    ABERTO = "aberto"
    EM_ANDAMENTO = "em_andamento"
    RESOLVIDO = "resolvido"
    FECHADO = "fechado"

class Categoria(StrEnum):
    INTEGRACAO = "integracao"
    COBRANCA = "cobranca"
    ACESSO = "acesso"
    OUTRO = "outro"

class Prioridade(StrEnum):
    BAIXA = "baixa"
    MEDIA = "media"
    ALTA = "alta"
    CRITICA = "critica"



class Ticket(SQLModel, table=True):
    __tablename__="tickets"
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    cliente_id: UUID = Field(foreign_key="clientes.id")
    agente_id: UUID | None = Field(default=None, foreign_key="agentes.id")
    titulo: str
    descricao: str
    status: StatusTicket = StatusTicket.ABERTO
    categoria: Categoria
    prioridade: Prioridade = Prioridade.MEDIA
    prazo_sla: datetime
    resolvido_em: datetime | None
    atualizado_em: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    criado_em: datetime = Field(default_factory= lambda: datetime.now(timezone.utc))

    cliente: "Cliente" = Relationship(
        back_populates="tickets"
    )

    agente: "Agente" = Relationship(
        back_populates="tickets"
    )

    comentarios: list["Comentario"] = Relationship(
        back_populates="ticket"
    )