# Configuração de Webhooks

**Categoria:** integracao
**Tipo:** manual
**Versão:** 1.4
**Última atualização:** 2026-07-20

---

## O que são Webhooks

Webhooks permitem que o Helpdesk notifique sistemas externos em tempo real quando eventos ocorrem na plataforma, eliminando a necessidade de polling periódico. Quando um evento é disparado, a plataforma envia uma requisição `POST` para a URL configurada com um payload JSON descrevendo o evento.

---

## Cadastro de URL

Acesse **Configurações → Integrações → Webhooks** e clique em **Novo Webhook**.

Campos obrigatórios:

| Campo | Descrição |
|---|---|
| **URL de destino** | Endpoint HTTPS que receberá os eventos. HTTP não é aceito. |
| **Eventos** | Selecione um ou mais eventos (ver lista abaixo) |
| **Secret** | Chave usada para assinar o payload (gerada automaticamente ou informada) |

---

## Eventos Disponíveis

| Evento | Disparado quando |
|---|---|
| `ticket.criado` | Um novo ticket é aberto |
| `ticket.atualizado` | Status, prioridade ou agente de um ticket mudam |
| `ticket.resolvido` | Ticket passa para status `resolvido` |
| `ticket.fechado` | Ticket passa para status `fechado` |
| `comentario.adicionado` | Um comentário público é adicionado ao ticket |
| `sla.proximo_vencimento` | SLA do ticket vence em menos de 2 horas |
| `sla.vencido` | Prazo de SLA ultrapassado sem resolução |

---

## Estrutura do Payload

```json
{
  "evento": "ticket.resolvido",
  "timestamp": "2026-10-10T14:32:00Z",
  "versao": "2",
  "dados": {
    "ticket_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
    "status_anterior": "em_andamento",
    "status_novo": "resolvido",
    "categoria": "integracao",
    "prioridade": "alta",
    "resolvido_em": "2026-10-10T14:32:00Z",
    "prazo_sla": "2026-10-11T10:00:00Z",
    "sla_cumprido": true
  }
}
```

---

## Verificação de Assinatura (HMAC)

Cada requisição inclui o cabeçalho `X-Helpdesk-Signature` com a assinatura HMAC-SHA256 do corpo da requisição usando o **secret** configurado.

### Como verificar em Python

```python
import hmac
import hashlib

def verificar_assinatura(payload_bytes: bytes, secret: str, assinatura_recebida: str) -> bool:
    esperado = hmac.new(
        secret.encode("utf-8"),
        payload_bytes,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={esperado}", assinatura_recebida)
```

> **Importante:** sempre use `hmac.compare_digest` para comparar assinaturas. Comparação direta com `==` é vulnerável a timing attacks.

---

## Política de Reenvio em Falha

Se o endpoint retornar um status diferente de `2xx` ou não responder em **10 segundos**, a plataforma tenta reenviar o evento com **backoff exponencial**:

| Tentativa | Intervalo |
|---|---|
| 1ª (original) | Imediato |
| 2ª | 1 minuto |
| 3ª | 5 minutos |
| 4ª | 30 minutos |
| 5ª | 2 horas |

Após 5 tentativas sem sucesso, o evento é marcado como **falho** e um alerta é enviado ao administrador da integração. O histórico de entregas fica disponível em **Configurações → Webhooks → Histórico** por 7 dias.

---

## Boas Práticas

- **Responda rapidamente:** retorne `200 OK` imediatamente ao receber o evento e processe em background. Processamentos longos causam timeout e reenvios desnecessários.
- **Trate duplicatas:** reenvios podem gerar o mesmo evento mais de uma vez. Use o campo `ticket_id` + `evento` + `timestamp` como chave de idempotência.
- **Filtre eventos:** cadastre apenas os eventos que seu sistema realmente consome para reduzir tráfego.
- **Monitore falhas:** configure alertas para webhooks com alta taxa de falha — pode indicar problema no seu endpoint ou mudança no formato do payload.

---

## Testando o Webhook

Na tela de configuração do webhook, clique em **Enviar evento de teste** para disparar um payload de exemplo para a URL cadastrada sem criar dados reais na plataforma.

Você também pode usar ferramentas como [webhook.site](https://webhook.site) para inspecionar payloads durante o desenvolvimento.
