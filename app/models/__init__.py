from app.models.clientes import Cliente, Planos
from app.models.agentes import Agente, Niveis
from app.models.tickets import Ticket, StatusTicket, Categoria, Prioridade
from app.models.comentarios import Comentario



__all__ = [
    "Cliente", "Planos",
    "Agente", "Niveis",
    "Ticket", "StatusTicket", "Categoria", "Prioridade",
    "Comentario",
]