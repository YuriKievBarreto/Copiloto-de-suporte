# Política de Escalonamento de Tickets

**Categoria:** outro
**Tipo:** politica
**Versão:** 2.3
**Última atualização:** 2026-09-20

---

## Objetivo

Esta política define quando e como um ticket deve ser escalado para um nível superior de suporte, os critérios de prioridade para escalonamento e os SLAs de resposta em cada nível.

---

## Níveis de Suporte

| Nível | Responsável | Escopo |
|---|---|---|
| **L1** | Agentes Junior/Trainee | Triagem inicial, problemas comuns, documentados em FAQ e manuais |
| **L2** | Agentes Pleno | Problemas técnicos intermediários, investigação aprofundada, configurações avançadas |
| **L3** | Agentes Sênior | Problemas críticos, bugs confirmados, integrações complexas, decisões de arquitetura |
| **L4** | Engenharia / Produto | Bugs de plataforma confirmados pelo L3, solicitações de mudança de produto |

---

## Quando Escalar

### Escalonamento obrigatório de L1 → L2

O agente L1 **deve** escalar quando:

- Não conseguir resolver o problema em até **50% do prazo de SLA**.
- O problema envolve configuração avançada não coberta pela documentação padrão.
- O cliente reporta impacto em múltiplos usuários ou sistemas críticos.
- O problema é recorrente (mesmo ticket aberto mais de uma vez no mesmo mês).
- O cliente solicita explicitamente falar com um nível superior.

### Escalonamento obrigatório de L2 → L3

O agente L2 **deve** escalar quando:

- O problema requer acesso a logs de sistema ou banco de dados de produção.
- A causa suspeita é um bug na plataforma.
- O problema persiste após 2 tentativas de solução documentadas no ticket.
- O SLA está em risco e a solução não está clara.
- O ticket envolve dados de clientes Enterprise com impacto financeiro direto.

### Escalonamento de L3 → L4 (Engenharia)

Realizado pelo L3 quando há confirmação de bug ou necessidade de alteração de produto. O L3 deve documentar:

- Passos para reprodução do bug.
- Logs relevantes.
- Impacto estimado (número de clientes afetados).
- Workaround disponível ou não.

---

## SLA de Resposta por Nível

O SLA de resposta é o tempo máximo para o agente do novo nível **fazer o primeiro contato** com o cliente após o escalonamento:

| Nível para onde vai | Prioridade Crítica | Prioridade Alta | Prioridade Média | Prioridade Baixa |
|---|---|---|---|---|
| **L2** | 30 min | 1 hora | 4 horas | 8 horas |
| **L3** | 15 min | 30 min | 2 horas | 4 horas |
| **L4** | 30 min | 2 horas | 1 dia útil | 3 dias úteis |

---

## Como Escalar um Ticket

1. No ticket, clique em **Ações → Escalar**.
2. Selecione o nível de destino (L2, L3 ou L4).
3. Preencha o campo obrigatório **Motivo do escalonamento** — seja específico:
   - ✅ "Cliente Enterprise com integração ERP falhando há 4h, causa não identificada após análise de logs"
   - ❌ "Não sei resolver"
4. Adicione uma nota interna com o histórico de investigação até o momento.
5. Confirme — o ticket é reatribuído automaticamente ao agente mais disponível do nível selecionado.

O cliente recebe notificação automática informando que o ticket foi escalonado para análise especializada.

---

## Escalonamento de Emergência (Crítico)

Para tickets **críticos** com impacto imediato em produção:

1. Escale normalmente pelo sistema.
2. **Adicionalmente**, acione o canal de emergência:
   - Chat interno: canal `#suporte-critico`
   - Telefone de plantão (disponível apenas para Enterprise): exibido no painel do gerente de conta.

Tickets críticos de clientes Enterprise devem ser acompanhados pelo L3 com **atualizações a cada 30 minutos** até a resolução.

---

## Responsabilidades após Escalonamento

- O agente que escalou **não abandona o ticket** — permanece como acompanhante e ponto de contato com o cliente.
- O agente do novo nível tem a propriedade técnica da investigação.
- Toda descoberta relevante deve ser documentada no ticket como **nota interna**.
- Após resolução, o agente L3/L2 deve documentar a causa raiz e a solução aplicada para enriquecer a base de conhecimento.
