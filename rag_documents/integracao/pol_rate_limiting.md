# Política de Rate Limiting e Timeouts

**Categoria:** integracao
**Tipo:** politica
**Versão:** 1.2
**Última atualização:** 2026-09-01

---

## Objetivo

Esta política define os limites de requisições por intervalo de tempo (rate limiting) e os tempos máximos de resposta (timeouts) aplicados à API REST do Helpdesk Copilot, diferenciados por plano de contrato.

---

## Limites de Requisições (Rate Limiting)

Os limites são aplicados **por credencial de integração** (client_id) e contados em janelas deslizantes de 60 segundos.

| Plano | Requisições / minuto | Requisições / hora | Requisições / dia |
|---|---|---|---|
| **Free** | 30 | 500 | 5.000 |
| **Pro** | 120 | 3.000 | 50.000 |
| **Enterprise** | 600 | 20.000 | Ilimitado* |

\* Enterprise possui limites diários negociáveis conforme contrato.

### Limites por Endpoint

Alguns endpoints possuem limites próprios independentes dos limites globais:

| Endpoint | Limite adicional |
|---|---|
| `POST /tickets` | 10 criações/minuto (todos os planos) |
| `GET /tickets` (listagem) | 5 req/s por IP |
| Autenticação (`/oauth/token`) | 10 req/minuto por client_id |

---

## Comportamento ao Atingir o Limite

Quando o limite é excedido, a API retorna:

```http
HTTP/1.1 429 Too Many Requests
Retry-After: 42
X-RateLimit-Limit: 120
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1728561600
```

| Cabeçalho | Significado |
|---|---|
| `Retry-After` | Segundos até poder tentar novamente |
| `X-RateLimit-Limit` | Limite configurado para o plano |
| `X-RateLimit-Remaining` | Requisições restantes na janela atual |
| `X-RateLimit-Reset` | Timestamp Unix em que a janela reinicia |

---

## Timeouts

| Operação | Free | Pro | Enterprise |
|---|---|---|---|
| Leitura simples (`GET /tickets/{id}`) | 10 s | 10 s | 10 s |
| Listagem com filtros | 15 s | 20 s | 30 s |
| Criação/atualização de ticket | 10 s | 10 s | 10 s |
| Exportação de dados em lote | 30 s | 60 s | 120 s |
| Sincronização com ERP (via webhook) | — | 30 s | 60 s |

Requisições que ultrapassam o timeout retornam `504 Gateway Timeout`. O servidor **não garante** que a operação foi concluída — verifique o estado do recurso com um `GET` antes de retentar.

---

## Recomendações de Implementação

### Retry com Backoff Exponencial

Implemente retry apenas para erros `429` e `5xx`. Para `4xx` (exceto 429), **não** tente novamente sem corrigir o problema.

Algoritmo recomendado:

```
espera = min(base * (2 ** tentativa) + jitter_aleatorio, maximo)
```

Valores sugeridos: `base = 1s`, `maximo = 60s`, `jitter = randint(0, 1000ms)`.

### Circuit Breaker

Para integrações críticas (Pro e Enterprise), implemente o padrão Circuit Breaker: após N falhas consecutivas, pare de enviar requisições por um período definido antes de tentar reabrir o circuito.

---

## Solicitação de Aumento de Limite

Clientes Pro e Enterprise podem solicitar aumento de limites via ticket de suporte com categoria `integracao` e prioridade `alta`. A análise é feita em até **2 dias úteis** para Pro e **4 horas** para Enterprise.

Inclua na solicitação:
- Justificativa de negócio
- Volume estimado de requisições por hora
- Endpoints críticos para a operação
