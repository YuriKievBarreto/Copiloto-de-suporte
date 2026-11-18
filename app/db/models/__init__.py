from app.db.models.clientes import Cliente, Planos
from app.db.models.agentes import Agente, Niveis
from app.db.models.tickets import Ticket, StatusTicket, Categoria, Prioridade
from app.db.models.comentarios import Comentario



__all__ = [
    "Cliente", "Planos",
    "Agente", "Niveis",
    "Ticket", "StatusTicket", "Categoria", "Prioridade",
    "Comentario",
]