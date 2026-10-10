# Gestão de Assinatura e Planos

**Categoria:** cobranca
**Tipo:** manual
**Versão:** 2.2
**Última atualização:** 2026-09-01

---

## Planos Disponíveis

| Recurso | Free | Pro | Enterprise |
|---|---|---|---|
| Usuários incluídos | 3 | 20 | Ilimitado |
| Tickets/mês | 100 | 2.000 | Ilimitado |
| SLA crítico | 8h | 4h | 2h |
| Suporte por chat | ❌ | ✅ | ✅ Dedicado |
| API com rate alto | ❌ | ✅ | ✅ |
| Relatórios avançados | ❌ | ✅ | ✅ |
| Gerente de conta | ❌ | ❌ | ✅ |

---

## Upgrade de Plano

### Como fazer

1. Acesse **Configurações → Assinatura → Alterar Plano**.
2. Selecione o plano desejado.
3. Confirme o novo valor e a data de vigência.

### Efeito na fatura

O upgrade é imediato — os novos limites e SLAs entram em vigor no momento da confirmação. A cobrança é **proporcional ao período restante do mês atual**:

```
Cobrança adicional = (Diferença de valor / Dias do mês) × Dias restantes
```

Na próxima fatura, o valor integral do novo plano é cobrado.

---

## Downgrade de Plano

### Como fazer

1. Acesse **Configurações → Assinatura → Alterar Plano**.
2. Selecione o plano inferior.
3. Confirme — o downgrade entra em vigor no **início do próximo ciclo de faturamento**.

### Efeito na fatura

O downgrade **não é imediato**: o plano atual permanece ativo até o fim do período pago. O valor não é reembolsado pelo período restante (exceto nos casos cobertos pela Política de Reembolso).

> **Atenção:** verifique se o uso atual está dentro dos limites do plano de destino. Dados, usuários ou tickets que excedam os limites do novo plano podem ficar inacessíveis.

---

## Cancelamento

### Como cancelar

1. Acesse **Configurações → Assinatura → Cancelar Assinatura**.
2. Informe o motivo (opcional, mas ajuda a melhorar o serviço).
3. Confirme o cancelamento.

O acesso continua disponível até o fim do período já pago. Após essa data, a conta é desativada e os dados ficam retidos por **30 dias** antes da exclusão permanente.

### Reativação

Para reativar uma conta cancelada dentro do período de 30 dias, acesse o portal com o e-mail de administrador e clique em **Reativar Conta**. Os dados são restaurados integralmente.

---

## Período de Carência

Assinaturas novas (primeiros 30 dias) têm **garantia de satisfação**: o cliente pode cancelar e receber reembolso integral sem necessidade de justificativa. Após esse período, o cancelamento segue as regras padrão.

---

## Faturamento

- O ciclo de faturamento é mensal, iniciando na data de contratação do plano.
- Faturas são emitidas no mesmo dia do mês da contratação.
- Boletos vencem em **5 dias úteis**. PIX e cartão são cobrados na data de emissão.
- Para receber a nota fiscal por e-mail, configure o destinatário em **Configurações → Dados Fiscais**.

---

## Cupons de Desconto

Cupons devem ser inseridos no campo **Código Promocional** durante a contratação ou em **Configurações → Assinatura → Aplicar Cupom**.

- Cupons têm validade definida — verifique a data de expiração antes de usar.
- Cupons de desconto percentual aplicam-se sobre o valor cheio do plano.
- Cupons não são acumuláveis entre si.
- Se o cupom não foi aplicado corretamente, abra um ticket de suporte com categoria `cobranca` incluindo o código e o print da tela.
