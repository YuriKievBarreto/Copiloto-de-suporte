# Perguntas Frequentes — Integrações

**Categoria:** integracao
**Tipo:** faq
**Versão:** 1.6
**Última atualização:** 2026-09-30

---

## Autenticação

**Por que estou recebendo erro 401 mesmo com o token correto?**

O token de acesso tem validade de 1 hora. Após esse período, qualquer requisição retorna `401 Unauthorized`. Implemente renovação automática: solicite um novo token quando `expires_in - tempo_decorrido < 60s`. Nunca reutilize um token expirado.

---

**O token OAuth2 expira antes do previsto. O que pode estar causando isso?**

Verifique se os relógios do servidor que gera a requisição e do servidor de autenticação estão sincronizados via NTP. Uma diferença de relógio superior a 5 minutos pode fazer com que o token seja considerado inválido ou expirado antes do tempo real. Além disso, confirme que está lendo o campo `expires_in` da resposta e não usando um valor fixo hardcoded.

---

**Posso usar o mesmo client_id para múltiplas integrações simultâneas?**

Tecnicamente sim, mas não é recomendado. O rate limiting é aplicado por client_id, então múltiplas integrações compartilham o mesmo pool de requisições. Crie credenciais separadas para cada sistema integrado acessando **Configurações → Integrações → Credenciais**.

---

## Webhooks

**O webhook está configurado mas não está disparando. O que verificar?**

1. Confirme que a URL de destino usa **HTTPS** (HTTP é rejeitado).
2. Acesse **Configurações → Webhooks → Histórico** e verifique se há tentativas com falha.
3. Certifique-se de que o endpoint retorna `2xx` em menos de 10 segundos.
4. Verifique se os eventos corretos foram selecionados no cadastro do webhook.
5. Teste manualmente usando o botão **Enviar evento de teste** na tela de configuração.

---

**Estou recebendo o mesmo evento várias vezes. É um bug?**

Não necessariamente. A plataforma reenvia eventos em caso de falha na entrega (veja a Política de Reenvio). Seu sistema deve ser **idempotente**: use a combinação `ticket_id + evento + timestamp` como chave para detectar e ignorar duplicatas.

---

## Payload e Campos

**Alguns campos esperados não estão chegando no payload da API. O que fazer?**

Verifique a versão da API que está utilizando (`/v1` vs `/v2`). Campos adicionados em versões mais recentes não estão disponíveis em versões antigas. Consulte o changelog da API em **Documentação → Changelog**. Se o campo deveria existir na versão atual, abra um ticket com categoria `integracao`.

---

**Por que estou vendo dados duplicados após a sincronização?**

Esse problema ocorre geralmente quando:
1. O sistema faz retry de uma operação `POST` sem verificar se a primeira tentativa foi bem-sucedida.
2. A integração não verifica se o registro já existe antes de criar um novo.

Use o campo `id` retornado pela API como identificador canônico. Antes de criar um registro, consulte com `GET /tickets?cliente_id=X&titulo=Y` para verificar se já existe.

---

## Erros Comuns

**Recebo erro 422 ao criar um ticket. O que significa?**

O erro `422 Unprocessable Entity` indica que o payload está sintaticamente correto (JSON válido) mas falhou em alguma validação de negócio. O corpo da resposta contém detalhes:

```json
{
  "erro": "validation_error",
  "detalhes": [
    {"campo": "categoria", "mensagem": "Valor 'billing' não é válido. Use: integracao, cobranca, acesso, outro"}
  ]
}
```

Verifique os valores aceitos pelos campos enum (`categoria`, `prioridade`, `status`).

---

**A sincronização com o ERP está falhando com timeout. Como resolver?**

Consulte a Solução documentada: **Caso Resolvido: Timeout na Sincronização com ERP**. Em resumo: verifique o pool de conexões do ERP, implemente retry com backoff exponencial e ajuste o parâmetro de keep-alive da conexão TCP. Se o problema persistir, abra um ticket com logs detalhados do erro.
