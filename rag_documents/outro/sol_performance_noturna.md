# Caso Resolvido: Degradação de Performance no Período Noturno

**Categoria:** outro
**Tipo:** solucao
**ID do caso original:** TKT-0731
**Data de resolução:** 2026-07-28
**Agente responsável:** Gabriela Nunes (Sênior)

---

## Descrição do Problema

O cliente relatou que a plataforma ficava significativamente mais lenta entre 22h e 3h, com tempos de resposta passando de menos de 1 segundo para 8–15 segundos em operações simples como carregar o dashboard e listar tickets. O problema ocorria todas as noites e afetava todos os usuários da conta, independente do navegador ou dispositivo.

**Sintomas relatados:**
- Dashboard demorava mais de 10 segundos para carregar os gráficos.
- Listagem de tickets retornava com timeout ocasional (`504 Gateway Timeout`).
- Exportação de relatórios falhava consistentemente nesse período.
- O problema desaparecia por completo a partir das 3h30.

---

## Investigação

### Etapa 1 — Descartando causas do lado do cliente

Testes realizados pelo agente confirmaram que:
- O problema ocorria em múltiplos dispositivos e redes diferentes.
- A latência de rede do cliente era normal.
- Outros clientes na mesma região geográfica não reportavam o problema — descartando problema de infraestrutura global.

**Conclusão:** o problema era específico da conta ou do ambiente de dados do cliente.

### Etapa 2 — Análise de logs da plataforma

Os logs de query do banco de dados mostraram que consultas normalmente rápidas (< 100ms) estavam demorando entre 5.000ms e 12.000ms exclusivamente no período noturno.

Queries mais afetadas:
```sql
-- Normalmente: 80ms | Noite: 9.200ms
SELECT * FROM tickets WHERE cliente_id = $1 ORDER BY criado_em DESC LIMIT 50;

-- Normalmente: 120ms | Noite: 11.500ms
SELECT COUNT(*), categoria FROM tickets GROUP BY categoria;
```

### Etapa 3 — Identificação da causa

Cruzando os horários de degradação com os jobs agendados no ambiente do cliente, foi identificado um **job de backup completo do banco de dados** configurado para executar diariamente às 22h, com duração média de 5 horas.

O backup realizava um `pg_dump` completo que:
1. Adquiria locks de leitura nas tabelas principais durante toda a execução.
2. Gerava I/O intenso no disco compartilhado entre o banco de dados e o servidor de aplicação.
3. Consumia até 80% da capacidade de leitura do disco, degradando todas as outras operações.

**Causa raiz:** competição de recursos entre o job de backup e as queries da aplicação, agravada pela configuração de disco compartilhado.

---

## Solução Aplicada

### 1. Reprogramação do job de backup

O backup foi movido para as **4h30**, horário de menor uso histórico da conta, reduzindo o sobreposição com o período de uso noturno.

### 2. Separação de volumes de disco

O banco de dados foi migrado para um volume de disco dedicado, independente do servidor de aplicação. Isso eliminou a competição de I/O entre o backup e as operações da aplicação.

### 3. Migração para backup incremental

O backup completo diário foi substituído por:
- **Backup incremental diário** às 4h30 (duração: ~20 minutos)
- **Backup completo semanal** aos domingos às 3h (duração: ~2 horas)

Isso reduziu o impacto do período de backup de 5 horas para menos de 30 minutos diários.

### 4. Criação de índice faltante

Durante a análise, foi identificado que a tabela `tickets` não tinha índice no campo `criado_em`, causando sequential scans em queries de listagem ordenada. O índice foi criado:

```sql
CREATE INDEX CONCURRENTLY idx_tickets_criado_em ON tickets (criado_em DESC);
CREATE INDEX CONCURRENTLY idx_tickets_cliente_id_criado_em ON tickets (cliente_id, criado_em DESC);
```

Isso reduziu o tempo das queries afetadas de 9.200ms para 85ms, mesmo durante o período de backup.

---

## Resultado

Após as mudanças:
- **Zero reclamações** de lentidão noturna nas 4 semanas seguintes.
- Tempo médio de resposta da API no período noturno: **95ms** (vs. 8–15 segundos antes).
- Tempo de backup diário reduzido de 5 horas para **22 minutos**.

---

## Recomendações Preventivas

- Sempre agende jobs de manutenção pesados (backup, reindexação, vacuum) no horário de **menor uso histórico** da conta — verifique os relatórios de acesso antes de definir o horário.
- Use volumes de disco separados para banco de dados e aplicação em ambientes que exigem alta disponibilidade.
- Monitore o tempo de execução de queries com `pg_stat_statements` e configure alertas para queries acima de 1 segundo.
- Prefira backups incrementais para reduzir o impacto operacional diário.
- Crie índices nas colunas usadas frequentemente em `ORDER BY`, `WHERE` e `JOIN` — especialmente em tabelas que crescem continuamente como `tickets` e `comentarios`.
