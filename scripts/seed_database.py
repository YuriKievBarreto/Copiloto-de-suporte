"""
scripts/seed_database.py
------------------------
Popula o banco de dados com dados sintéticos para o Copiloto de Suporte.

Execução:
    python -m scripts.seed_database              # popula normalmente
    python -m scripts.seed_database --limpar     # apaga tudo e repopula (pede confirmação)

Reprodutibilidade:
    Semente padrão: SEED=42 (sobrescreva via variável de ambiente SEED=<int>)
    Os dados gerados são determinísticos para a mesma semente.

Regras de SLA (prazo_sla a partir de criado_em):
    Prioridade  | Free     | Pro      | Enterprise
    ------------+----------+----------+----------
    baixa       | 120 h    | 72 h     | 48 h
    media       | 72 h     | 48 h     | 24 h
    alta        | 24 h     | 12 h     | 8 h
    critica     | 8 h      | 4 h      | 2 h
"""

import argparse
import logging
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlmodel import Session, select

# garante que o pacote raiz está no path quando rodado como módulo
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.models  # noqa: F401  — registra todos os modelos no metadata
from app.core.database import get_engine
from app.models.agentes import Agente, Niveis
from app.models.clientes import Cliente, Planos
from app.models.comentarios import Comentario
from app.models.tickets import Categoria, Prioridade, StatusTicket, Ticket

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuração
# ---------------------------------------------------------------------------

SEED: int = int(os.environ.get("SEED", 42))

# Volumes
N_CLIENTES = 30
N_AGENTES = 8
N_TICKETS = 120   # ~4 por cliente em média
N_COMENTARIOS_MIN = 1
N_COMENTARIOS_MAX = 5

# Prazo SLA em horas: SLA_HORAS[prioridade][plano]
SLA_HORAS: dict[Prioridade, dict[Planos, int]] = {
    Prioridade.BAIXA:   {Planos.FREE: 120, Planos.PRO: 72,  Planos.ENTERPRISE: 48},
    Prioridade.MEDIA:   {Planos.FREE: 72,  Planos.PRO: 48,  Planos.ENTERPRISE: 24},
    Prioridade.ALTA:    {Planos.FREE: 24,  Planos.PRO: 12,  Planos.ENTERPRISE: 8},
    Prioridade.CRITICA: {Planos.FREE: 8,   Planos.PRO: 4,   Planos.ENTERPRISE: 2},
}

# ---------------------------------------------------------------------------
# Dados fictícios
# ---------------------------------------------------------------------------

NOMES_EMPRESAS = [
    "Acme Corp", "Globo Tech", "NovaSoft", "DataBridge", "CloudNine",
    "ByteForge", "NetPulse", "PixelStream", "CoreLogic", "SyncHub",
    "Infraworks", "VaultSys", "OpenFlow", "DevPath", "LinkNode",
    "TurboPay", "MeshNet", "EdgeSync", "Querida Tech", "Apex Labs",
    "Orbit Solutions", "BluePeak", "FastLoop", "IronChain", "SoftWave",
    "NexaBit", "GridOps", "PrimeStack", "AgileBridge", "ZeroLag",
]

NOMES_AGENTES = [
    "Ana Lima", "Bruno Souza", "Carla Menezes", "Diego Rocha",
    "Elisa Ferreira", "Felipe Castro", "Gabriela Nunes", "Henrique Alves",
]

DOMINIOS_EMPRESA = [n.lower().replace(" ", "").replace(".", "") for n in NOMES_EMPRESAS]

TITULOS_POR_CATEGORIA: dict[Categoria, list[str]] = {
    Categoria.INTEGRACAO: [
        "Falha na integração via API REST",
        "Webhook não está disparando eventos",
        "Timeout na sincronização com ERP",
        "Erro 401 ao autenticar na API",
        "Dados duplicados após sync",
        "Integração com Zapier retorna 500",
        "Campos ausentes no payload de retorno",
        "OAuth2 expira antes do esperado",
    ],
    Categoria.COBRANCA: [
        "Cobrança duplicada no cartão",
        "Fatura com valor incorreto",
        "Não recebi o boleto do mês",
        "Reembolso não foi processado",
        "Assinatura cancelada mas cobrança continua",
        "Cupom de desconto não aplicado",
        "Nota fiscal com dados errados",
        "Plano downgrade não refletiu na fatura",
    ],
    Categoria.ACESSO: [
        "Não consigo redefinir a senha",
        "Usuário bloqueado sem motivo aparente",
        "MFA não aceita o código gerado",
        "Conta desativada após migração",
        "Permissões de administrador removidas",
        "SSO retorna erro de configuração",
        "Sessão expira em menos de 1 minuto",
        "Novo usuário não recebeu e-mail de convite",
    ],
    Categoria.OUTRO: [
        "Dashboard não carrega os gráficos",
        "Relatório exportado está vazio",
        "Notificações por e-mail pararam de chegar",
        "Performance degradada no período noturno",
        "Erro genérico ao salvar configuração",
        "Módulo de auditoria não registra ações",
        "Upload de arquivo falha acima de 5 MB",
        "Tradução incorreta na interface",
    ],
}

DESCRICOES_EXTRAS = [
    "O problema começou após a última atualização do sistema.",
    "Ocorre de forma intermitente, principalmente no período da manhã.",
    "Já tentamos limpar o cache e o problema persiste.",
    "O erro aparece apenas para usuários com perfil de administrador.",
    "Afeta todos os usuários da conta, não só um específico.",
    "Reproduzido em ambiente de homologação também.",
    "O suporte anterior sugeriu aguardar, mas o problema continua.",
    "Impacta diretamente o faturamento da empresa.",
    "Urgente: clientes finais estão sendo afetados.",
    "Registrado também no painel de status externo.",
]

COMENTARIOS_TEMPLATES = [
    "Recebemos o relato e iniciamos a investigação.",
    "Conseguimos reproduzir o problema em nosso ambiente de testes.",
    "Solicitamos logs adicionais ao cliente para análise.",
    "O time de engenharia foi acionado para verificar.",
    "Identificamos a causa raiz: {causa}. Trabalhando na correção.",
    "Correção aplicada em produção. Aguardamos confirmação do cliente.",
    "Cliente confirmou que o problema foi resolvido.",
    "Fechando o ticket após confirmação de resolução.",
    "Escalando para o nível sênior devido à complexidade.",
    "Nota interna: verificar se outros clientes do mesmo plano foram afetados.",
    "Reaberto pelo cliente — problema voltou após 2 dias.",
    "Aplicado workaround temporário enquanto correção definitiva é desenvolvida.",
]

CAUSAS = [
    "misconfiguration no timeout da conexão",
    "race condition no processo de sincronização",
    "certificado SSL expirado",
    "índice corrompido no banco",
    "bug introduzido na versão 2.4.1",
    "limite de rate-limit atingido",
    "campo obrigatório ausente no payload",
    "problema de encoding UTF-8",
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

NOW = datetime.now(timezone.utc)


def ago(days: int = 0, hours: int = 0) -> datetime:
    return NOW - timedelta(days=days, hours=hours)


def calcular_prazo_sla(criado_em: datetime, prioridade: Prioridade, plano: Planos) -> datetime:
    horas = SLA_HORAS[prioridade][plano]
    return criado_em + timedelta(hours=horas)


def gerar_email_cliente(nome_empresa: str, dominio: str) -> str:
    return f"suporte@{dominio}.com.br"


def gerar_email_agente(nome: str) -> str:
    partes = nome.lower().split()
    return f"{partes[0]}.{partes[-1]}@helpdesk.interno"


# ---------------------------------------------------------------------------
# Geradores de dados
# ---------------------------------------------------------------------------

def gerar_clientes(rng: random.Random) -> list[Cliente]:
    clientes = []
    planos_pool = (
        [Planos.FREE] * 12 + [Planos.PRO] * 12 + [Planos.ENTERPRISE] * 6
    )
    for i in range(N_CLIENTES):
        nome = NOMES_EMPRESAS[i]
        dominio = DOMINIOS_EMPRESA[i]
        plano = planos_pool[i]
        criado_em = ago(days=rng.randint(60, 365))
        clientes.append(Cliente(
            id=uuid4(),
            nome=nome,
            email=gerar_email_cliente(nome, dominio),
            plano=plano,
            created_at=criado_em,
        ))
    return clientes


def gerar_agentes(rng: random.Random) -> list[Agente]:
    niveis_pool = [Niveis.TRAINEE, Niveis.JUNIOR, Niveis.JUNIOR,
                   Niveis.PLENO, Niveis.PLENO, Niveis.PLENO,
                   Niveis.SENIOR, Niveis.SENIOR]
    agentes = []
    for i, nome in enumerate(NOMES_AGENTES):
        criado_em = ago(days=rng.randint(90, 400))
        agentes.append(Agente(
            id=uuid4(),
            nome=nome,
            email=gerar_email_agente(nome),
            nivel=niveis_pool[i],
            ativo=True,
            created_at=criado_em,
        ))
    return agentes


def gerar_tickets(
    rng: random.Random,
    clientes: list[Cliente],
    agentes: list[Agente],
) -> list[Ticket]:
    tickets = []

    # Distribuição de tickets por cliente: alguns têm muito, outros poucos
    pesos_clientes = [rng.randint(1, 10) for _ in clientes]
    total_peso = sum(pesos_clientes)
    contagens = [max(1, round(N_TICKETS * p / total_peso)) for p in pesos_clientes]

    # Garante cenários: pelo menos 1 ticket por categoria e prioridade
    categorias_pool = list(Categoria) * (N_TICKETS // len(Categoria) + 1)
    prioridades_pool = (
        [Prioridade.BAIXA] * 25 +
        [Prioridade.MEDIA] * 50 +
        [Prioridade.ALTA] * 30 +
        [Prioridade.CRITICA] * 15
    )
    rng.shuffle(categorias_pool)
    rng.shuffle(prioridades_pool)

    ticket_idx = 0
    for cliente, contagem in zip(clientes, contagens):
        for _ in range(contagem):
            if ticket_idx >= N_TICKETS:
                break

            categoria = categorias_pool[ticket_idx % len(categorias_pool)]
            prioridade = prioridades_pool[ticket_idx % len(prioridades_pool)]
            titulo = rng.choice(TITULOS_POR_CATEGORIA[categoria])
            descricao_extra = rng.choice(DESCRICOES_EXTRAS)
            descricao = f"{titulo}. {descricao_extra}"

            criado_em = ago(days=rng.randint(0, 45), hours=rng.randint(0, 23))
            prazo_sla = calcular_prazo_sla(criado_em, prioridade, cliente.plano)

            # Decide status com pesos realistas
            r = rng.random()
            if r < 0.25:
                status = StatusTicket.ABERTO
                agente_id = None
                resolvido_em = None
                atualizado_em = criado_em + timedelta(minutes=rng.randint(5, 60))
            elif r < 0.45:
                status = StatusTicket.EM_ANDAMENTO
                agente_id = rng.choice(agentes).id
                resolvido_em = None
                atualizado_em = criado_em + timedelta(hours=rng.randint(1, 12))
            elif r < 0.80:
                status = StatusTicket.RESOLVIDO
                agente_id = rng.choice(agentes).id
                # Alguns resolvidos dentro, outros fora do SLA
                if rng.random() < 0.75:
                    # dentro do prazo
                    horas_sla = SLA_HORAS[prioridade][cliente.plano]
                    resolvido_em = criado_em + timedelta(hours=rng.uniform(0.5, horas_sla * 0.9))
                else:
                    # fora do prazo (violação)
                    horas_sla = SLA_HORAS[prioridade][cliente.plano]
                    resolvido_em = criado_em + timedelta(hours=rng.uniform(horas_sla * 1.1, horas_sla * 2))
                atualizado_em = resolvido_em
            else:
                status = StatusTicket.FECHADO
                agente_id = rng.choice(agentes).id
                horas_sla = SLA_HORAS[prioridade][cliente.plano]
                resolvido_em = criado_em + timedelta(hours=rng.uniform(0.5, horas_sla))
                atualizado_em = resolvido_em + timedelta(hours=rng.randint(1, 24))

            tickets.append(Ticket(
                id=uuid4(),
                cliente_id=cliente.id,
                agente_id=agente_id,
                titulo=titulo,
                descricao=descricao,
                status=status,
                categoria=categoria,
                prioridade=prioridade,
                prazo_sla=prazo_sla,
                resolvido_em=resolvido_em,
                atualizado_em=atualizado_em,
                criado_em=criado_em,
            ))
            ticket_idx += 1

    return tickets


def gerar_comentarios(
    rng: random.Random,
    tickets: list[Ticket],
    agentes: list[Agente],
) -> list[Comentario]:
    comentarios = []
    for ticket in tickets:
        n = rng.randint(N_COMENTARIOS_MIN, N_COMENTARIOS_MAX)
        agentes_disponiveis = agentes if agentes else []
        if not agentes_disponiveis:
            continue

        criado_base = ticket.criado_em
        for i in range(n):
            agente = rng.choice(agentes_disponiveis)
            template = rng.choice(COMENTARIOS_TEMPLATES)
            conteudo = template.format(causa=rng.choice(CAUSAS)) if "{causa}" in template else template

            # Comentários internos são minoria
            interno = rng.random() < 0.2

            # Comentários em ordem cronológica
            offset_horas = rng.uniform(0.5, 4) * (i + 1)
            criado_em = criado_base + timedelta(hours=offset_horas)

            # Não ultrapassa NOW
            if criado_em > NOW:
                criado_em = NOW - timedelta(minutes=rng.randint(1, 30))

            comentarios.append(Comentario(
                id=uuid4(),
                ticket_id=ticket.id,
                agente_id=agente.id,
                conteudo=conteudo,
                interno=interno,
                criado_em=criado_em,
            ))
    return comentarios


# ---------------------------------------------------------------------------
# Persistência
# ---------------------------------------------------------------------------

def banco_esta_vazio(session: Session) -> bool:
    return session.exec(select(Cliente)).first() is None


def limpar_banco(session: Session) -> None:
    log.warning("Apagando todos os dados existentes...")
    for model in (Comentario, Ticket, Agente, Cliente):
        registros = session.exec(select(model)).all()
        for r in registros:
            session.delete(r)
    session.commit()
    log.info("Banco limpo.")


def seed(limpar: bool = False) -> None:
    engine = get_engine()
    rng = random.Random(SEED)

    with Session(engine) as session:
        if limpar:
            limpar_banco(session)
        elif not banco_esta_vazio(session):
            log.info(
                "Banco já contém dados. Use --limpar para apagar e repopular. "
                "Nenhum dado foi inserido."
            )
            return

        log.info("Gerando dados com semente SEED=%d ...", SEED)

        clientes = gerar_clientes(rng)
        agentes = gerar_agentes(rng)
        tickets = gerar_tickets(rng, clientes, agentes)
        comentarios = gerar_comentarios(rng, tickets, agentes)

        log.info(
            "Inserindo: %d clientes, %d agentes, %d tickets, %d comentários",
            len(clientes), len(agentes), len(tickets), len(comentarios),
        )

        try:
            session.add_all(clientes)
            session.flush()
            session.add_all(agentes)
            session.flush()
            session.add_all(tickets)
            session.flush()
            session.add_all(comentarios)
            session.commit()
            log.info("✅  População concluída com sucesso.")
        except Exception:
            session.rollback()
            log.exception("❌  Erro durante a inserção. Transação revertida.")
            raise


# ---------------------------------------------------------------------------
# Validação
# ---------------------------------------------------------------------------

def validar(session: Session) -> None:
    from sqlmodel import func

    log.info("── Validação ────────────────────────────────────────")

    # Contagens
    for model, label in [
        (Cliente, "clientes"),
        (Agente, "agentes"),
        (Ticket, "tickets"),
        (Comentario, "comentários"),
    ]:
        total = session.exec(select(func.count()).select_from(model)).one()
        log.info("  %-15s %d registros", label, total)

    # Distribuição de status
    log.info("── Status dos tickets ───────────────────────────────")
    for status in StatusTicket:
        total = session.exec(
            select(func.count()).select_from(Ticket).where(Ticket.status == status)
        ).one()
        log.info("  %-20s %d", status, total)

    # Violações de SLA (resolvido_em > prazo_sla)
    violacoes = session.exec(
        select(func.count()).select_from(Ticket).where(
            Ticket.resolvido_em != None,  # noqa: E711
            Ticket.resolvido_em > Ticket.prazo_sla,
        )
    ).one()
    log.info("── SLA ──────────────────────────────────────────────")
    log.info("  Violações de SLA (resolvidos fora do prazo): %d", violacoes)

    # Tickets críticos abertos
    criticos_abertos = session.exec(
        select(func.count()).select_from(Ticket).where(
            Ticket.prioridade == Prioridade.CRITICA,
            Ticket.status.in_([StatusTicket.ABERTO, StatusTicket.EM_ANDAMENTO]),
        )
    ).one()
    log.info("  Tickets críticos ainda abertos: %d", criticos_abertos)

    log.info("── Distribuição por categoria ───────────────────────")
    for cat in Categoria:
        total = session.exec(
            select(func.count()).select_from(Ticket).where(Ticket.categoria == cat)
        ).one()
        log.info("  %-15s %d tickets", cat, total)

    log.info("── Distribuição por plano ───────────────────────────")
    for plano in Planos:
        total = session.exec(
            select(func.count()).select_from(Cliente).where(Cliente.plano == plano)
        ).one()
        log.info("  %-15s %d clientes", plano, total)

    log.info("─────────────────────────────────────────────────────")


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Popula o banco de dados com dados sintéticos."
    )
    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Apaga todos os dados existentes antes de popular (pede confirmação).",
    )
    parser.add_argument(
        "--validar",
        action="store_true",
        default=True,
        help="Executa validações após a população (padrão: true).",
    )
    args = parser.parse_args()

    if args.limpar:
        confirmacao = input(
            "⚠️  Isso apagará TODOS os dados do banco. Digite 'sim' para confirmar: "
        )
        if confirmacao.strip().lower() != "sim":
            log.info("Operação cancelada.")
            return

    seed(limpar=args.limpar)

    if args.validar:
        engine = get_engine()
        with Session(engine) as session:
            validar(session)


if __name__ == "__main__":
    main()
