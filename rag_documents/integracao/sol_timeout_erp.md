# Caso Resolvido: Timeout na Sincronização com ERP

**Categoria:** integracao
**Tipo:** solucao
**ID do caso original:** TKT-0482
**Data de resolução:** 2026-06-14
**Agente responsável:** Felipe Castro (Sênior)

---

## Descrição do Problema

O cliente relatou que o processo de sincronização entre o sistema interno e o ERP falhava sistematicamente com erro de timeout após aproximadamente 30 segundos. O problema ocorria com maior frequência entre 22h e 2h, horário de menor movimento, e afetava apenas sincronizações com volume acima de 500 registros.

**Mensagem de erro reportada:**

```
ConnectionError: HTTPSConnectionPool(host='erp.cliente.interno', port=443):
Read timed out. (read timeout=30)
```

**Impacto:** dados desatualizados no painel de gestão, divergência entre o sistema de tickets e o ERP, retrabalho manual para reconciliação.

---

## Investigação

### Hipóteses Levantadas

1. Timeout de rede configurado abaixo do necessário para volumes grandes
2. Pool de conexões TCP esgotado no servidor do ERP
3. Job de backup noturno competindo pelos mesmos recursos do banco do ERP
4. Certificado SSL causando renegociação lenta

### Evidências Coletadas

- **Logs do cliente:** confirmaram que o timeout ocorria exatamente em 30s — valor padrão da biblioteca HTTP usada, não configurado explicitamente.
- **Métricas do ERP:** entre 22h e 2h, o servidor de banco do ERP atingia 95% de uso de CPU devido a um job de backup completo agendado para esse horário.
- **Teste com volume reduzido:** sincronizações com menos de 100 registros funcionavam normalmente no mesmo horário, confirmando que o problema era de recursos, não de rede.
- **Análise de conexões TCP:** o pool de conexões do ERP estava configurado com máximo de 10 conexões simultâneas — valor inadequado para sincronizações em lote.

---

## Causa Raiz

**Duas causas combinadas:**

1. **Pool de conexões insuficiente no ERP:** o limite de 10 conexões simultâneas causava fila de espera que, somada ao tempo de processamento do volume grande, ultrapassava o timeout de 30s.
2. **Concorrência com job de backup:** o backup noturno consumia a maior parte dos recursos do servidor do ERP exatamente no horário em que a sincronização era executada.

---

## Solução Aplicada

### 1. Ajuste do timeout na integração

O timeout de leitura foi aumentado de 30s para 120s, e um timeout de conexão separado foi definido para 10s:

```python
import httpx

client = httpx.Client(
    timeout=httpx.Timeout(connect=10.0, read=120.0, write=30.0, pool=5.0)
)
```

### 2. Implementação de retry com backoff exponencial

```python
import time
import random

def sync_com_erp(payload, max_tentativas=4):
    for tentativa in range(max_tentativas):
        try:
            resposta = client.post("/erp/sync", json=payload)
            resposta.raise_for_status()
            return resposta.json()
        except (httpx.TimeoutException, httpx.HTTPStatusError) as e:
            if tentativa == max_tentativas - 1:
                raise
            espera = min(2 ** tentativa + random.uniform(0, 1), 60)
            time.sleep(espera)
```

### 3. Reprogramação do job de backup do ERP

O job de backup foi movido para as 4h, horário de menor carga simultânea, eliminando a concorrência de recursos.

### 4. Aumento do pool de conexões do ERP

O pool de conexões foi aumentado de 10 para 50 conexões simultâneas, configuração adequada para o volume de sincronização do cliente.

### 5. Keep-alive TCP habilitado

```python
client = httpx.Client(
    timeout=httpx.Timeout(connect=10.0, read=120.0),
    limits=httpx.Limits(max_keepalive_connections=20, keepalive_expiry=30)
)
```

---

## Resultado

Após as alterações, **zero falhas de timeout** foram registradas nas duas semanas seguintes ao ajuste. O tempo médio de sincronização para 500+ registros caiu de falha recorrente para **18 segundos** em média.

---

## Recomendações Preventivas

- Configure timeouts explicitamente em toda integração — nunca confie no valor padrão da biblioteca.
- Monitore o horário dos jobs de manutenção do ERP e evite agendar sincronizações no mesmo período.
- Implemente alertas para sincronizações que levem mais de 60% do timeout configurado — sinal precoce de degradação.
- Documente o pool de conexões máximo do sistema externo e planeje a capacidade de acordo.
