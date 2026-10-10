# Política de Reembolso

**Categoria:** cobranca
**Tipo:** politica
**Versão:** 3.1
**Última atualização:** 2026-08-01

---

## Objetivo

Esta política define as condições, prazos e procedimentos para solicitação e processamento de reembolsos na plataforma Helpdesk Copilot.

---

## Condições de Elegibilidade

Um reembolso pode ser solicitado nas seguintes situações:

| Situação | Elegível | Observações |
|---|---|---|
| Cobrança duplicada (mesmo valor, mesmo período) | ✅ Sim | Reembolso integral automático após confirmação |
| Cobrança após cancelamento da assinatura | ✅ Sim | Reembolso proporcional ao período não utilizado |
| Downgrade de plano com cobrança do plano anterior | ✅ Sim | Diferença proporcional ao período restante |
| Insatisfação com o serviço (primeiros 30 dias) | ✅ Sim | Garantia de satisfação — reembolso integral |
| Insatisfação com o serviço (após 30 dias) | ❌ Não | Fora do período de garantia |
| Não utilização do serviço | ❌ Não | A assinatura é cobrada independente do uso |
| Cupom não aplicado corretamente | ✅ Sim | Reembolso da diferença após análise |

---

## Prazo de Processamento

| Método de Pagamento | Prazo para Estorno |
|---|---|
| Cartão de crédito | Até **10 dias úteis** (podendo aparecer na próxima fatura) |
| Boleto bancário | Até **5 dias úteis** (via transferência para conta cadastrada) |
| PIX | Até **2 dias úteis** |
| Nota fiscal | Emitida nota de cancelamento em até **5 dias úteis** |

> O prazo começa a contar após a **confirmação da elegibilidade** pelo time de cobrança, não a partir da abertura do ticket.

---

## Como Solicitar um Reembolso

1. Acesse o portal ou abra um ticket de suporte com:
   - **Categoria:** `cobranca`
   - **Prioridade:** `alta` (cobrança indevida) ou `media` (demais casos)
2. Inclua no ticket:
   - Número da fatura ou comprovante de pagamento
   - Valor a ser reembolsado
   - Motivo detalhado
   - Dados bancários para reembolso (se boleto ou PIX)
3. O time de cobrança analisa em até **2 dias úteis** (Pro/Enterprise) ou **5 dias úteis** (Free).
4. Após aprovação, o estorno é iniciado conforme os prazos acima.

---

## Reembolsos Parciais

Em casos de downgrade ou cancelamento parcial do período, o reembolso é calculado **pro rata temporis**:

```
Valor reembolsado = (Valor pago / Dias do período) × Dias não utilizados
```

**Exemplo:** assinatura Pro de R$ 300/mês cancelada no dia 10 de um mês de 30 dias:

```
Reembolso = (300 / 30) × 20 = R$ 200,00
```

---

## Casos Não Cobertos

- Cobranças de períodos já encerrados há mais de **90 dias**.
- Situações em que o cliente utilizou o serviço normalmente e solicita reembolso sem justificativa válida.
- Cobranças relacionadas a serviços adicionais contratados separadamente (consulte a política específica desses serviços).

---

## Escalamento

Se o reembolso não for processado dentro do prazo estipulado ou houver divergência no valor, o ticket deve ser escalado para o nível sênior. Clientes Enterprise têm direito a contato direto com o gerente de conta para casos de reembolso acima de R$ 1.000,00.
