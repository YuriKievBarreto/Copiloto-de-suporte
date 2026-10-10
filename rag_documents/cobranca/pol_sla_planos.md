# Política de SLA por Plano

**Categoria:** cobranca
**Tipo:** politica
**Versão:** 2.0
**Última atualização:** 2026-09-15

---

## Objetivo

Esta política define os Acordos de Nível de Serviço (SLA) para atendimento de tickets de suporte, diferenciados por plano de contrato e prioridade do ticket.

---

## Prazos de Resolução por Prioridade e Plano

O prazo de SLA é contado a partir do momento de **abertura do ticket** e representa o tempo máximo até a resolução completa.

| Prioridade | Free | Pro | Enterprise |
|---|---|---|---|
| 🟢 **Baixa** | 120 horas | 72 horas | 48 horas |
| 🟡 **Média** | 72 horas | 48 horas | 24 horas |
| 🟠 **Alta** | 24 horas | 12 horas | 8 horas |
| 🔴 **Crítica** | 8 horas | 4 horas | 2 horas |

> Prazos contam em horas corridas (24/7), não apenas em horário comercial.

---

## Critérios de Prioridade

A prioridade é definida pelo cliente no momento da abertura, mas pode ser ajustada pelo agente com justificativa:

| Prioridade | Critério |
|---|---|
| **Crítica** | Serviço completamente indisponível; impacto em todos os usuários; perda financeira direta |
| **Alta** | Funcionalidade crítica degradada; impacto em grupo de usuários; sem workaround disponível |
| **Média** | Funcionalidade não crítica afetada; workaround disponível; impacto limitado |
| **Baixa** | Dúvida, melhoria ou problema cosmético sem impacto operacional |

---

## Penalidades por Violação de SLA

Quando o prazo de SLA é ultrapassado sem resolução, o cliente tem direito a créditos conforme o plano:

### Plano Pro

| Atraso em relação ao SLA | Crédito |
|---|---|
| Até 50% acima do prazo | 10% do valor mensal do plano |
| De 50% a 100% acima do prazo | 25% do valor mensal do plano |
| Acima de 100% do prazo | 50% do valor mensal do plano |

### Plano Enterprise

| Atraso em relação ao SLA | Crédito |
|---|---|
| Até 25% acima do prazo | 15% do valor mensal do plano |
| De 25% a 75% acima do prazo | 35% do valor mensal do plano |
| Acima de 75% do prazo | 75% do valor mensal do plano |

> O plano **Free** não tem direito a créditos por violação de SLA.

---

## Como Solicitar Crédito por Violação de SLA

1. Identifique o ticket com SLA violado (o campo `resolvido_em` é posterior ao `prazo_sla`).
2. Abra um novo ticket com:
   - **Categoria:** `cobranca`
   - **Prioridade:** `media`
   - Número do ticket original
   - Data de abertura e resolução
3. O time de cobrança analisa e aplica os créditos em até **5 dias úteis**.

Créditos são aplicados na próxima fatura e não são convertíveis em dinheiro.

---

## Exclusões de SLA

O prazo de SLA é suspenso nos seguintes casos:

- **Aguardando resposta do cliente:** quando o agente solicita informações e o cliente não responde em até 24h, o SLA fica pausado até a resposta.
- **Manutenção programada:** janelas de manutenção anunciadas com pelo menos 48h de antecedência não contam no prazo.
- **Causa externa:** falhas em infraestrutura de terceiros (cloud providers, operadoras) fora do controle da plataforma.
- **Força maior:** situações extraordinárias documentadas.

---

## Monitoramento

Clientes Pro e Enterprise têm acesso ao painel de SLA em tempo real em **Relatórios → SLA**, com visualização de:

- Tickets dentro do prazo
- Tickets em risco (>75% do prazo consumido)
- Tickets com SLA vencido
- Taxa histórica de cumprimento de SLA por categoria e agente
