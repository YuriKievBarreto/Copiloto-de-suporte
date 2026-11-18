"""
scripts/seed_database.py
------------------------
Popula o PostgreSQL com dados sintéticos realistas para o Copiloto de Suporte.

Especificações do Projeto:
    - ~200 clientes (distribuição Free, Pro e Enterprise)
    - 15 agentes de suporte (Trainee a Sênior)
    - ~2.000 tickets categorizados com alta variabilidade semântica
    - Histórico de comentários progressivos com notas internas e técnicas
    - Total alinhamento semântico com os 18 documentos RAG em rag_documents/
    - Regras de negócio e prazos de SLA calculados por prioridade e plano

Execução:
    python -m scripts.seed_database              # popula normalmente (~2.000 tickets)
    python -m scripts.seed_database --limpar     # apaga tudo e repopula (com confirmação)

Reprodutibilidade:
    Semente padrão: SEED=42 (personalizável via variável de ambiente SEED=<int>)
"""

import argparse
import logging
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from sqlmodel import Session, select, func

# Garante o diretório raiz no PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import app.db.models  # noqa: F401 — Registra todos os modelos no SQLAlchemy metadata
from app.infra.database.relational_database import get_engine
from app.db.models.agentes import Agente, Niveis
from app.db.models.clientes import Cliente, Planos
from app.db.models.comentarios import Comentario
from app.db.models.tickets import Categoria, Prioridade, StatusTicket, Ticket

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configurações de Volume e Parâmetros
# ---------------------------------------------------------------------------

SEED: int = int(os.environ.get("SEED", 42))

N_CLIENTES = 200
N_AGENTES = 15
N_TICKETS = 2000
N_COMENTARIOS_MIN = 1
N_COMENTARIOS_MAX = 5

# Tabela Oficial de SLA em horas (prioridade x plano)
# Baseada em rag_documents/cobranca/pol_sla_planos.md
SLA_HORAS: dict[Prioridade, dict[Planos, int]] = {
    Prioridade.BAIXA:   {Planos.FREE: 120, Planos.PRO: 72,  Planos.ENTERPRISE: 48},
    Prioridade.MEDIA:   {Planos.FREE: 72,  Planos.PRO: 48,  Planos.ENTERPRISE: 24},
    Prioridade.ALTA:    {Planos.FREE: 24,  Planos.PRO: 12,  Planos.ENTERPRISE: 8},
    Prioridade.CRITICA: {Planos.FREE: 8,   Planos.PRO: 4,   Planos.ENTERPRISE: 2},
}

NOW = datetime.now(timezone.utc)


def ago(days: int = 0, hours: int = 0, minutes: int = 0) -> datetime:
    return NOW - timedelta(days=days, hours=hours, minutes=minutes)


def calcular_prazo_sla(criado_em: datetime, prioridade: Prioridade, plano: Planos) -> datetime:
    horas = SLA_HORAS[prioridade][plano]
    return criado_em + timedelta(hours=horas)


# ---------------------------------------------------------------------------
# Catálogo de Empresas e Agentes
# ---------------------------------------------------------------------------

PREFIXOS_EMPRESA = [
    "Tech", "Data", "Cloud", "Net", "Byte", "Soft", "Sync", "Cyber", "Nexus",
    "Omni", "Vanguard", "Apex", "Nova", "Prime", "Global", "Alpha", "Hyper",
    "Matrix", "Quantum", "Pulse", "Core", "Info", "Link", "Logic", "Meta",
    "Smart", "Agile", "Flow", "Bridge", "Node", "Vault", "Mesh", "Scale",
    "Aero", "Bright", "Delta", "Echo", "Flux", "Horizon", "Infinity", "Krypton"
]

SUFIXOS_EMPRESA = [
    "Labs", "Systems", "Solutions", "Group", "Digital", "Networks", "Logistics",
    "Pay", "Finance", "Health", "Analytics", "Services", "Media", "Retail",
    "Energy", "Security", "Studio", "Works", "Hub", "Partners", "Ventures",
    "Tech", "Industries", "Cloud", "Software", "Consulting", "Dynamics"
]

NOMES_AGENTES = [
    ("Ana Lima", Niveis.SENIOR),
    ("Bruno Souza", Niveis.PLENO),
    ("Carla Menezes", Niveis.SENIOR),
    ("Diego Rocha", Niveis.PLENO),
    ("Elisa Ferreira", Niveis.JUNIOR),
    ("Felipe Castro", Niveis.SENIOR),
    ("Gabriela Nunes", Niveis.SENIOR),
    ("Henrique Alves", Niveis.PLENO),
    ("Isabela Santos", Niveis.JUNIOR),
    ("João Pedro Costa", Niveis.JUNIOR),
    ("Karina Oliveira", Niveis.PLENO),
    ("Lucas Martins", Niveis.TRAINEE),
    ("Mariana Dias", Niveis.PLENO),
    ("Natan Ribeiro", Niveis.JUNIOR),
    ("Patricia Lima", Niveis.TRAINEE),
]

# ---------------------------------------------------------------------------
# Motor Semântico: Geradores de Cenários Baseados em rag_documents/
# ---------------------------------------------------------------------------

ENDPOINTS_API = ["/v2/tickets", "/v2/clientes", "/v2/tickets/{id}/comentarios", "/oauth/token"]
PROVEDORES_SSO = ["Microsoft Azure AD (Entra ID)", "Google Workspace", "Okta SAML", "ADFS Local"]
NAVEGADORES = ["Google Chrome 128", "Mozilla Firefox 130", "Microsoft Edge 128", "Safari 17.5"]
EXTENSOES_ANUNCIO = ["uBlock Origin", "AdBlock Plus", "Privacy Badger"]
ERROS_ERP = ["Read timed out (30s)", "HTTPSConnectionPool Max retries exceeded", "Connection reset by peer"]


def gerar_cenario_integracao(rng: random.Random) -> tuple[str, str, list[str]]:
    """Cenários baseados em: man_api_rest.md, man_webhooks.md, pol_rate_limiting.md, sol_timeout_erp.md, faq_integracoes.md"""
    tipo = rng.choice(["erp_timeout", "rate_limit", "oauth_401", "webhook_hmac", "webhook_missing", "v1_deprecation"])

    if tipo == "erp_timeout":
        erro = rng.choice(ERROS_ERP)
        registros = rng.choice([450, 780, 1200, 2500])
        titulo = f"Falha de sincronização com ERP: {erro}"
        desc = (
            f"O processo de integração em lote enviando {registros} registros falhou com '{erro}' "
            "durante a janela noturna. O sistema não conclui a reconciliação e retorna 504 Gateway Timeout."
        )
        solucoes = [
            "Conforme documentado em sol_timeout_erp.md, identificado pool de conexões do ERP esgotado e conflito com job de backup.",
            "Aumentamos o timeout de leitura para 120s e implementamos retry com backoff exponencial na biblioteca httpx.",
            "Recomendamos migrar a rotina pesada para as 04h30 para evitar contenção de CPU e I/O no ERP."
        ]
    elif tipo == "rate_limit":
        limite = rng.choice(["30 req/min (Free)", "120 req/min (Pro)"])
        endpoint = rng.choice(ENDPOINTS_API)
        titulo = f"Erro HTTP 429 Too Many Requests no endpoint {endpoint}"
        desc = (
            f"Nossa rotina de coleta automática passou a receber status 429 no endpoint {endpoint}. "
            f"O cabeçalho Retry-After está retornando valores de {rng.randint(20, 55)} segundos."
        )
        solucoes = [
            f"A credencial do cliente atingiu o teto da Política de Rate Limiting ({limite}).",
            "Orientado a respeitar o cabeçalho Retry-After e implementar algoritmo com jitter para chamadas paralelas.",
            "Cliente informado sobre a possibilidade de upgrade para Enterprise com limites dedicados."
        ]
    elif tipo == "oauth_401":
        titulo = "Erro 401 Unauthorized após 1 hora de execução contínua"
        desc = (
            "A integração via API REST para de funcionar exatamente após 60 minutos com a mensagem "
            "'Invalid or expired access token'. Precisamos reiniciar o worker para restabelecer."
        )
        solucoes = [
            "O token OAuth2 possui tempo de expiração fixo de 3600 segundos (1 hora), conforme man_api_rest.md.",
            "Orientado o time de engenharia do cliente a verificar o campo 'expires_in' e solicitar novo token preventivamente a cada 55 minutos."
        ]
    elif tipo == "webhook_hmac":
        titulo = "Falha na validação de assinatura HMAC do webhook (X-Helpdesk-Signature)"
        desc = (
            "Configuramos nosso endpoint receptor HTTPS, mas a validação do hash SHA-256 está falhando "
            "sistematicamente com divergência de assinatura."
        )
        solucoes = [
            "Conforme man_webhooks.md, o cabeçalho X-Helpdesk-Signature inclui o prefixo 'sha256=' antes do hash hexadecimal.",
            "Também orientamos a utilização de hmac.compare_digest em Python para evitar vulnerabilidade de timing attack.",
            "Cliente ajustou o parser do payload raw e a verificação passou a retornar True."
        ]
    elif tipo == "webhook_missing":
        evento = rng.choice(["ticket.resolvido", "sla.vencido", "comentario.adicionado"])
        titulo = f"Webhook do evento '{evento}' não é disparado após atualização"
        desc = (
            f"Atualizamos os tickets pelo painel, mas o evento '{evento}' não chega na URL cadastrada. "
            "Gostaríamos de verificar o histórico de tentativas com falha."
        )
        solucoes = [
            "Verificamos no histórico de webhooks que o endpoint de destino retornava timeout > 10 segundos.",
            "A política de reenvio tentou 5 vezes com backoff exponencial antes de suspender.",
            "Recomendamos que o receptor retorne 200 OK imediatamente e processe os dados de forma assíncrona."
        ]
    else:
        titulo = "Campos de payload ausentes na chamada GET /tickets"
        desc = "As propriedades 'prazo_sla' e 'categoria' não constam no JSON retornado pela API."
        solucoes = [
            "A chamada estava apontando para a rota legada /v1 da API REST.",
            "Orientamos a alteração da URL base para /v2, onde os campos de SLA e governança estão totalmente disponíveis."
        ]

    return titulo, desc, solucoes


def gerar_cenario_cobranca(rng: random.Random) -> tuple[str, str, list[str]]:
    """Cenários baseados em: pol_reembolso.md, pol_sla_planos.md, man_assinatura_planos.md, faq_cobranca.md"""
    tipo = rng.choice(["duplicada", "estorno_sla", "reembolso_downgrade", "boleto_atraso", "cupom_falha", "nfe_cnpj"])

    if tipo == "duplicada":
        valor = rng.choice(["R$ 150,00", "R$ 350,00", "R$ 890,00"])
        titulo = f"Cobrança duplicada de {valor} na fatura do cartão de crédito"
        desc = (
            f"Identificamos dois lançamentos idênticos de {valor} no mesmo mês referentes à assinatura. "
            "Solicitamos estorno imediato do débito excedente."
        )
        solucoes = [
            "Confirmada cobrança duplicada por falha momentânea de comunicação com a adquirente.",
            "Conforme a Política de Reembolso (pol_reembolso.md), o estorno integral foi autorizado.",
            "O prazo para o crédito constar na fatura do cartão é de até 10 dias úteis."
        ]
    elif tipo == "estorno_sla":
        horas_atraso = rng.choice([6, 14, 28])
        titulo = f"Solicitação de crédito na fatura por violação de SLA ({horas_atraso}h de atraso)"
        desc = (
            f"Nosso ticket crítico anterior ultrapassou o SLA em {horas_atraso} horas. "
            "Solicitamos o desconto compensatório previsto no contrato do plano."
        )
        solucoes = [
            "Auditoria confirmou atraso superior a 50% em ticket crítico, violando o acordo de nível de serviço.",
            "Aplicado crédito compensatório de 35% no próximo ciclo de faturamento conforme a Política de SLA por Plano.",
            "Crédito refletirá na fatura emitida no próximo dia 10."
        ]
    elif tipo == "reembolso_downgrade":
        titulo = "Solicitação de reembolso proporcional (pró-rata) após downgrade"
        desc = (
            "Alteramos nosso plano de Enterprise para Pro no 8º dia do ciclo e gostaríamos de "
            "reaver o valor correspondente aos dias não utilizados."
        )
        solucoes = [
            "Conforme man_assinatura_planos.md e a Política de Reembolso, o cálculo foi feito pró-rata temporis.",
            "A diferença apurada foi convertida em saldo de crédito para as mensalidades seguintes."
        ]
    elif tipo == "boleto_atraso":
        titulo = "Boleto de faturamento mensal não recebido por e-mail"
        desc = (
            "A fatura vence em 3 dias úteis e o setor financeiro ainda não recebeu o código de barras ou PDF."
        )
        solucoes = [
            "Identificado que o e-mail cadastrado em Dados Fiscais estava desatualizado.",
            "Endereço corrigido e segunda via do boleto enviada com data de vencimento prorrogada."
        ]
    elif tipo == "cupom_falha":
        titulo = "Cupom de desconto promocional não aplicado na renovação"
        desc = "Inserimos o código promocional de 20% no portal, mas a fatura foi gerada no valor cheio."
        solucoes = [
            "Validado que o cupom estava ativo e era elegível para o plano.",
            "Ajuste manual aplicado no sistema financeiro e gerada nova fatura com o abatimento correto."
        ]
    else:
        titulo = "Nota fiscal de prestação de serviços emitida com CNPJ incorreto"
        desc = "A NF-e do mês passado foi faturada com os dados da nossa filial antiga em vez da matriz."
        solucoes = [
            "Dados cadastrais corrigidos em Configurações -> Dados Fiscais.",
            "Emitida nota de cancelamento e gerada a nova NF-e no prazo legal de 5 dias úteis."
        ]

    return titulo, desc, solucoes


def gerar_cenario_acesso(rng: random.Random) -> tuple[str, str, list[str]]:
    """Cenários baseados em: man_redefinicao_senha.md, man_mfa.md, man_sso.md, pol_bloqueio_contas.md, faq_acesso.md"""
    tipo = rng.choice(["mfa_totp", "sso_acs", "bloqueio_5_tentativas", "reset_expirado", "mfa_emergencia", "convite_novo"])

    if tipo == "mfa_totp":
        titulo = "Código de verificação TOTP do app autenticador recusado"
        desc = (
            "Ao inserir os 6 dígitos gerados no Google Authenticator ou Microsoft Authenticator, "
            "a plataforma exibe 'Código inválido ou expirado'."
        )
        solucoes = [
            "Conforme man_mfa.md, o algoritmo TOTP (RFC 6238) depende de sincronia estrita de relógio.",
            "Orientamos o usuário a ativar a opção 'Horário automático da rede' nas configurações do smartphone.",
            "Após sincronizar o horário, o código foi aceito imediatamente no primeiro teste."
        ]
    elif tipo == "sso_acs":
        idp = rng.choice(PROVEDORES_SSO)
        titulo = f"Erro de integração SAML 2.0 no Single Sign-On ({idp})"
        desc = (
            f"Usuários corporativos recebem erro de autenticação ao tentar logar via {idp}. "
            "A tela de login falha no redirecionamento para o ACS."
        )
        solucoes = [
            "Identificada divergência na Assertion Consumer Service URL (ACS URL) cadastrada no IdP.",
            "Removida barra invertida excedente no Entity ID e reimportado o arquivo de metadados XML.",
            "Single Sign-On normalizado para todos os colaboradores do domínio corporativo."
        ]
    elif tipo == "bloqueio_5_tentativas":
        titulo = "Conta bloqueada após 5 tentativas consecutivas de senha incorreta"
        desc = (
            "Colaborador tentou autenticar com senha antiga e o acesso foi travado. "
            "Necessitamos de desbloqueio urgente para continuidade operacional."
        )
        solucoes = [
            "Conta entrou em bloqueio temporário de 30 minutos conforme pol_bloqueio_contas.md.",
            "Administrador efetuou o desbloqueio manual e gerou um link de redefinição de senha seguro.",
            "Usuário cadastrou nova senha respeitando o requisito de 12 caracteres e caracteres especiais."
        ]
    elif tipo == "reset_expirado":
        titulo = "Link do e-mail de redefinição de senha acusa expiração"
        desc = "O usuário recebeu a mensagem com o botão de redefinição, mas ao clicar o portal informa que o link não é mais válido."
        solucoes = [
            "Conforme man_redefinicao_senha.md, links de redefinição possuem expiração estrita de 30 minutos por segurança.",
            "Disparado novo link com validade imediata e solicitado acesso em aba privativa."
        ]
    elif tipo == "mfa_emergencia":
        titulo = "Solicitação de desativação emergencial de MFA por perda de aparelho celular"
        desc = "O diretor de operações perdeu o dispositivo móvel com os autenticadores e não armazenou os 10 códigos de recuperação."
        solucoes = [
            "Executado o procedimento de 'Desativar MFA de Emergência' com dupla validação do administrador.",
            "Ação registrada no log de auditoria imutável.",
            "Usuário instruído a configurar novo segundo fator no primeiro login."
        ]
    else:
        titulo = "Novo usuário não recebeu e-mail de convite de primeiro acesso"
        desc = "Cadastramos um novo analista no portal, mas o link de ativação da conta não foi entregue."
        solucoes = [
            "Reenviado convite com prazo de 72 horas em Configurações -> Usuários.",
            "Solicitado ao time de TI do cliente inclusão do remetente @helpdesk.interno na whitelist do antispam."
        ]

    return titulo, desc, solucoes


def gerar_cenario_outro(rng: random.Random) -> tuple[str, str, list[str]]:
    """Cenários baseados em: pol_escalonamento.md, man_relatorios_auditoria.md, faq_plataforma.md, sol_performance_noturna.md"""
    tipo = rng.choice(["performance_noturna", "dashboard_graficos", "upload_5mb", "escalonamento_l3", "auditoria_retencao", "notificacao_diaria"])

    if tipo == "performance_noturna":
        titulo = "Lentidão acentuada no dashboard e timeouts entre 22h e 03h"
        desc = (
            "A equipe de monitoramento noturno relata lentidão de 8 a 15 segundos para abrir tickets e "
            "erros 504 Gateway Timeout recorrentes após as 22h."
        )
        solucoes = [
            "Conforme sol_performance_noturna.md, detectada disputa de I/O em disco causada por rotina de backup (pg_dump).",
            "Job de backup reprogramado para as 04h30 e criados índices dedicados em tickets(criado_em DESC).",
            "Tempo de resposta das consultas retornou para menos de 95ms durante toda a madrugada."
        ]
    elif tipo == "dashboard_graficos":
        navegador = rng.choice(NAVEGADORES)
        adblock = rng.choice(EXTENSOES_ANUNCIO)
        titulo = f"Painel de gráficos do Dashboard em branco no navegador {navegador}"
        desc = f"Os quadros de métricas de SLA e volume de tickets abertos não renderizam no {navegador}."
        solucoes = [
            f"Identificado bloqueio dos scripts de renderização pelo plugin {adblock}.",
            "Adicionada regra de exceção para a URL da plataforma e esvaziado o cache com Ctrl+Shift+R."
        ]
    elif tipo == "upload_5mb":
        titulo = "Falha ao anexar arquivo de evidências maior que 5 MB no ticket"
        desc = "Tentamos enviar uma gravação de tela de 8 MB em formato ZIP e a plataforma interrompe o upload com erro genérico."
        solucoes = [
            "Conforme man_relatorios_auditoria.md, anexos diretos possuem limite de 5 MB nos planos Free e Pro.",
            "Orientamos o cliente a compactar o vídeo ou utilizar link compartilhado seguro."
        ]
    elif tipo == "escalonamento_l3":
        titulo = "Solicitação de escalonamento para nível L3 (Engenharia) por reincidência"
        desc = "Mesmo problema operacional reaberto pela terceira vez no mesmo mês sem solução definitiva no atendimento L1/L2."
        solucoes = [
            "Ticket escalado diretamente para suporte L3 (Sênior) com base na Política de Escalonamento (pol_escalonamento.md).",
            "Tempo de resposta garantido em menos de 30 minutos e envolvimento do time de Produto."
        ]
    elif tipo == "auditoria_retencao":
        titulo = "Exportação de Log de Auditoria corta registros anteriores a 30 dias"
        desc = "Tentamos exportar o relatório de acessos dos últimos 90 dias mas o arquivo CSV gerado contém apenas o último mês."
        solucoes = [
            "O plano Free possui retenção máxima de log de auditoria de 30 dias (man_relatorios_auditoria.md).",
            "Explicamos que retenção estendida de 12 meses está disponível no plano Pro e 5 anos no Enterprise."
        ]
    else:
        titulo = "Alertas de atualização de tickets pararam de ser entregues por e-mail"
        desc = "Agentes pararam de receber e-mails automáticos quando um cliente responde no ticket."
        solucoes = [
            "Preferências de notificação foram alteradas acidentalmente para o modo 'Resumo diário consolidado'.",
            "Opção de envio em tempo real restaurada em Perfil -> Notificações."
        ]

    return titulo, desc, solucoes


# ---------------------------------------------------------------------------
# Geradores das Entidades
# ---------------------------------------------------------------------------

def gerar_empresas(rng: random.Random, n: int) -> list[dict[str, str]]:
    empresas = []
    nomes_usados = set()
    while len(empresas) < n:
        pref = rng.choice(PREFIXOS_EMPRESA)
        suf = rng.choice(SUFIXOS_EMPRESA)
        nome = f"{pref} {suf}"
        if nome not in nomes_usados:
            nomes_usados.add(nome)
            dominio = f"{pref.lower()}{suf.lower()}.com.br"
            empresas.append({"nome": nome, "dominio": dominio})
    return empresas


def gerar_clientes(rng: random.Random) -> list[Cliente]:
    empresas = gerar_empresas(rng, N_CLIENTES)
    clientes = []

    # Distribuição equilibrada: 60% Free (120), 30% Pro (60), 10% Enterprise (20)
    planos_dist = (
        [Planos.FREE] * 120 +
        [Planos.PRO] * 60 +
        [Planos.ENTERPRISE] * 20
    )
    rng.shuffle(planos_dist)

    for i, emp in enumerate(empresas):
        criado_em = ago(days=rng.randint(60, 365), hours=rng.randint(1, 23))
        clientes.append(Cliente(
            id=uuid4(),
            nome=emp["nome"],
            email=f"suporte@{emp['dominio']}",
            plano=planos_dist[i],
            created_at=criado_em,
        ))
    return clientes


def gerar_agentes(rng: random.Random) -> list[Agente]:
    agentes = []
    for nome, nivel in NOMES_AGENTES:
        partes = nome.lower().split()
        email = f"{partes[0]}.{partes[-1]}@helpdesk.interno"
        criado_em = ago(days=rng.randint(180, 400))
        agentes.append(Agente(
            id=uuid4(),
            nome=nome,
            email=email,
            nivel=nivel,
            ativo=True,
            created_at=criado_em,
        ))
    return agentes


def gerar_tickets_e_comentarios(
    rng: random.Random,
    clientes: list[Cliente],
    agentes: list[Agente],
) -> tuple[list[Ticket], list[Comentario]]:
    tickets = []
    comentarios = []

    # Separa agentes por senioridade para atribuição coerente
    agentes_juniores = [a for a in agentes if a.nivel in (Niveis.TRAINEE, Niveis.JUNIOR)]
    agentes_plenos = [a for a in agentes if a.nivel == Niveis.PLENO]
    agentes_seniores = [a for a in agentes if a.nivel == Niveis.SENIOR]

    # Distribuição de tickets por cliente via pesos (clientes Enterprise e Pro abrem mais tickets)
    pesos_clientes = []
    for c in clientes:
        if c.plano == Planos.ENTERPRISE:
            pesos_clientes.append(rng.randint(15, 25))
        elif c.plano == Planos.PRO:
            pesos_clientes.append(rng.randint(8, 15))
        else:
            pesos_clientes.append(rng.randint(2, 6))

    total_peso = sum(pesos_clientes)
    tickets_por_cliente = [max(1, round(N_TICKETS * p / total_peso)) for p in pesos_clientes]

    # Ajuste fino para cravar exatamente N_TICKETS
    diferenca = N_TICKETS - sum(tickets_por_cliente)
    for i in range(abs(diferenca)):
        idx = i % len(tickets_por_cliente)
        tickets_por_cliente[idx] += 1 if diferenca > 0 else -1

    prioridades_pool = (
        [Prioridade.BAIXA] * 35 +
        [Prioridade.MEDIA] * 45 +
        [Prioridade.ALTA] * 15 +
        [Prioridade.CRITICA] * 5
    )

    categorias = list(Categoria)

    for cliente, quant in zip(clientes, tickets_por_cliente):
        for _ in range(quant):
            categoria = rng.choice(categorias)
            prioridade = rng.choice(prioridades_pool)

            # Seleciona o gerador semântico correspondente
            if categoria == Categoria.INTEGRACAO:
                titulo, desc, solucoes_padrao = gerar_cenario_integracao(rng)
            elif categoria == Categoria.COBRANCA:
                titulo, desc, solucoes_padrao = gerar_cenario_cobranca(rng)
            elif categoria == Categoria.ACESSO:
                titulo, desc, solucoes_padrao = gerar_cenario_acesso(rng)
            else:
                titulo, desc, solucoes_padrao = gerar_cenario_outro(rng)

            # Idade do ticket: entre 0 e 60 dias atrás
            criado_em = ago(days=rng.randint(0, 60), hours=rng.randint(0, 23), minutes=rng.randint(0, 59))
            prazo_sla = calcular_prazo_sla(criado_em, prioridade, cliente.plano)
            horas_sla = SLA_HORAS[prioridade][cliente.plano]

            # Distribuição de status: ~15% Aberto, ~20% Em Andamento, ~55% Resolvido, ~10% Fechado
            r = rng.random()
            if r < 0.15:
                status = StatusTicket.ABERTO
                agente = None
                resolvido_em = None
                atualizado_em = criado_em + timedelta(minutes=rng.randint(5, 45))
            elif r < 0.35:
                status = StatusTicket.EM_ANDAMENTO
                agente = rng.choice(agentes_seniores if prioridade == Prioridade.CRITICA else agentes)
                resolvido_em = None
                atualizado_em = criado_em + timedelta(hours=rng.randint(1, 10))
            elif r < 0.90:
                status = StatusTicket.RESOLVIDO
                agente = rng.choice(agentes_seniores if prioridade in (Prioridade.CRITICA, Prioridade.ALTA) else agentes)

                # 80% dentro do prazo SLA / 20% violação estourando o SLA
                if rng.random() < 0.80:
                    resolvido_em = criado_em + timedelta(hours=rng.uniform(0.2, horas_sla * 0.85))
                else:
                    resolvido_em = criado_em + timedelta(hours=rng.uniform(horas_sla * 1.15, horas_sla * 2.2))

                # Garante que resolvido_em não ultrapasse o tempo presente
                if resolvido_em > NOW:
                    resolvido_em = NOW - timedelta(minutes=rng.randint(5, 30))

                atualizado_em = resolvido_em
            else:
                status = StatusTicket.FECHADO
                agente = rng.choice(agentes)
                resolvido_em = criado_em + timedelta(hours=rng.uniform(0.5, horas_sla * 0.9))
                if resolvido_em > NOW:
                    resolvido_em = NOW - timedelta(hours=rng.randint(1, 5))
                atualizado_em = resolvido_em + timedelta(hours=rng.randint(2, 48))
                if atualizado_em > NOW:
                    atualizado_em = NOW - timedelta(minutes=5)

            ticket_id = uuid4()
            ticket = Ticket(
                id=ticket_id,
                cliente_id=cliente.id,
                agente_id=agente.id if agente else None,
                titulo=titulo,
                descricao=desc,
                status=status,
                categoria=categoria,
                prioridade=prioridade,
                prazo_sla=prazo_sla,
                resolvido_em=resolvido_em,
                atualizado_em=atualizado_em,
                criado_em=criado_em,
            )
            tickets.append(ticket)

            # Geração do histórico encadeado de comentários
            num_comentarios = rng.randint(N_COMENTARIOS_MIN, N_COMENTARIOS_MAX)
            tempo_cursor = criado_em

            for idx in range(num_comentarios):
                delta_horas = rng.uniform(0.3, 3.5)
                tempo_cursor = tempo_cursor + timedelta(hours=delta_horas)

                # Comentários nunca podem ultrapassar resolvido_em ou NOW
                limite_tempo = resolvido_em if resolvido_em else NOW
                if tempo_cursor > limite_tempo:
                    tempo_cursor = limite_tempo - timedelta(minutes=rng.randint(2, 15))

                # Papel do agente no comentário baseado na progressão
                if idx == 0:
                    # Triagem inicial
                    agente_comentario = rng.choice(agentes_juniores) if agentes_juniores else rng.choice(agentes)
                    conteudo = "Ticket recebido e triado. Logs preliminares coletados para reprodução."
                    interno = False
                elif idx == 1 and prioridade in (Prioridade.ALTA, Prioridade.CRITICA):
                    # Escalonamento com nota interna
                    agente_comentario = rng.choice(agentes_plenos) if agentes_plenos else rng.choice(agentes)
                    conteudo = "Nota interna: escalando ticket para suporte L3 conforme Política de Escalonamento (pol_escalonamento.md)."
                    interno = True
                elif idx == num_comentarios - 1 and status in (StatusTicket.RESOLVIDO, StatusTicket.FECHADO):
                    # Solução final citando o procedimento correto
                    agente_comentario = agente if agente else rng.choice(agentes_seniores)
                    conteudo = rng.choice(solucoes_padrao)
                    interno = False
                else:
                    # Investigação em andamento
                    agente_comentario = rng.choice(agentes)
                    conteudo = rng.choice([
                        "Testes executados em ambiente de homologação confirmando o cenário relatado.",
                        "Solicitamos confirmação ao cliente se o comportamento persiste após as orientações.",
                        "Nota interna: checando dependências de rede e limites contratuais da conta.",
                        "Configuração validada com sucesso pelo analista responsável."
                    ])
                    interno = (rng.random() < 0.20)

                comentarios.append(Comentario(
                    id=uuid4(),
                    ticket_id=ticket_id,
                    agente_id=agente_comentario.id,
                    conteudo=conteudo,
                    interno=interno,
                    criado_em=tempo_cursor,
                ))

    return tickets, comentarios


# ---------------------------------------------------------------------------
# Persistência em Lote e Limpeza
# ---------------------------------------------------------------------------

def banco_esta_vazio(session: Session) -> bool:
    return session.exec(select(Cliente)).first() is None


def limpar_banco(session: Session) -> None:
    log.warning("Limpando dados existentes do banco...")
    for model in (Comentario, Ticket, Agente, Cliente):
        registros = session.exec(select(model)).all()
        for r in registros:
            session.delete(r)
    session.commit()
    log.info("Base de dados limpa com sucesso.")


def inserir_em_lote(session: Session, registros: list, tamanho_lote: int = 500) -> None:
    for i in range(0, len(registros), tamanho_lote):
        lote = registros[i : i + tamanho_lote]
        session.add_all(lote)
        session.flush()


def seed(limpar: bool = False) -> None:
    engine = get_engine()
    rng = random.Random(SEED)

    with Session(engine) as session:
        if limpar:
            limpar_banco(session)
        elif not banco_esta_vazio(session):
            log.info("O banco de dados já possui dados. Use --limpar para substituir.")
            return

        log.info("🚀 Iniciando geração de dados sintéticos (SEED=%d)...", SEED)

        clientes = gerar_clientes(rng)
        agentes = gerar_agentes(rng)
        tickets, comentarios = gerar_tickets_e_comentarios(rng, clientes, agentes)

        log.info(
            "Persistindo: %d clientes, %d agentes, %d tickets, %d comentários...",
            len(clientes), len(agentes), len(tickets), len(comentarios),
        )

        try:
            inserir_em_lote(session, clientes)
            inserir_em_lote(session, agentes)
            inserir_em_lote(session, tickets)
            inserir_em_lote(session, comentarios)
            session.commit()
            log.info("✅ População da base relacional concluída com êxito!")
        except Exception:
            session.rollback()
            log.exception("❌ Falha na transação. Rollback executado.")
            raise


# ---------------------------------------------------------------------------
# Bateria de Validação Diagnóstica
# ---------------------------------------------------------------------------

def validar(session: Session) -> None:
    log.info("═════════════════════════════════════════════════════════════")
    log.info("📊 DIAGNÓSTICO DA BASE RELACIONAL POPULADA")
    log.info("═════════════════════════════════════════════════════════════")

    # Contagens gerais
    for model, label in [
        (Cliente, "Clientes"),
        (Agente, "Agentes"),
        (Ticket, "Tickets"),
        (Comentario, "Comentários"),
    ]:
        total = session.exec(select(func.count()).select_from(model)).one()
        log.info("  %-16s : %d", label, total)

    # Distribuição por status
    log.info("─────────────────────────────────────────────────────────────")
    log.info("📌 Status dos Tickets:")
    for status in StatusTicket:
        tot = session.exec(select(func.count()).select_from(Ticket).where(Ticket.status == status)).one()
        pct = (tot / N_TICKETS) * 100
        log.info("  %-20s : %4d (%.1f%%)", status, tot, pct)

    # Métricas de SLA
    log.info("─────────────────────────────────────────────────────────────")
    log.info("⏱️  Conformidade de SLA:")
    resolvidos_total = session.exec(
        select(func.count()).select_from(Ticket).where(Ticket.resolvido_em != None)  # noqa: E711
    ).one()
    violacoes = session.exec(
        select(func.count()).select_from(Ticket).where(
            Ticket.resolvido_em != None,  # noqa: E711
            Ticket.resolvido_em > Ticket.prazo_sla,
        )
    ).one()
    pct_viol = (violacoes / resolvidos_total) * 100 if resolvidos_total else 0
    log.info("  Tickets Resolvidos       : %d", resolvidos_total)
    log.info("  Violações de SLA         : %d (%.1f%% fora do prazo)", violacoes, pct_viol)

    criticos_abertos = session.exec(
        select(func.count()).select_from(Ticket).where(
            Ticket.prioridade == Prioridade.CRITICA,
            Ticket.status.in_([StatusTicket.ABERTO, StatusTicket.EM_ANDAMENTO]),
        )
    ).one()
    log.info("  Críticos ainda Abertos   : %d", criticos_abertos)

    # Distribuição por Categoria
    log.info("─────────────────────────────────────────────────────────────")
    log.info("📂 Tickets por Categoria:")
    for cat in Categoria:
        tot = session.exec(select(func.count()).select_from(Ticket).where(Ticket.categoria == cat)).one()
        log.info("  %-16s : %d", cat, tot)

    # Distribuição de Clientes por Plano
    log.info("─────────────────────────────────────────────────────────────")
    log.info("🏢 Clientes por Plano:")
    for plano in Planos:
        tot = session.exec(select(func.count()).select_from(Cliente).where(Cliente.plano == plano)).one()
        log.info("  %-16s : %d", plano, tot)

    log.info("═════════════════════════════════════════════════════════════")


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Popula o banco de dados com dados sintéticos alinhados ao RAG."
    )
    parser.add_argument(
        "--limpar",
        action="store_true",
        help="Apaga todos os dados existentes antes de repopular.",
    )
    args = parser.parse_args()

    if args.limpar:
        confirmacao = input(
            "⚠️  ATENÇÃO: Isso apagará TODOS os dados do banco relacional. Digite 'sim' para continuar: "
        )
        if confirmacao.strip().lower() != "sim":
            log.info("Operação cancelada pelo usuário.")
            return

    seed(limpar=args.limpar)

    engine = get_engine()
    with Session(engine) as session:
        validar(session)


if __name__ == "__main__":
    main()
