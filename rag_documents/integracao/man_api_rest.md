# Guia de Integração via API REST

**Categoria:** integracao
**Tipo:** manual
**Versão:** 2.3
**Última atualização:** 2026-08-15

---

## Visão Geral

A API REST do Helpdesk Copilot permite que sistemas externos consultem e gerenciem tickets, clientes e agentes de forma programática. Todas as requisições devem ser feitas via HTTPS. Requisições em HTTP simples são rejeitadas com status `301 Moved Permanently`.

Base URL:

```
https://api.helpdesk.interno/v2
```

---

## Autenticação

A API utiliza **OAuth 2.0 com Client Credentials Flow** para integrações máquina-a-máquina.

### Obtendo o token de acesso

```http
POST https://auth.helpdesk.interno/oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=SEU_CLIENT_ID
&client_secret=SEU_CLIENT_SECRET
&scope=tickets:read tickets:write
```

**Resposta:**

```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "scope": "tickets:read tickets:write"
}
```

O token expira em **1 hora**. Implemente renovação automática antes da expiração para evitar erros `401 Unauthorized`.

### Usando o token

Inclua o token no cabeçalho `Authorization` de todas as requisições:

```http
Authorization: Bearer eyJhbGciOiJSUzI1NiIs...
```

---

## Endpoints Principais

### Tickets

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/tickets` | Lista tickets com paginação e filtros |
| `GET` | `/tickets/{id}` | Retorna um ticket pelo ID |
| `POST` | `/tickets` | Cria um novo ticket |
| `PATCH` | `/tickets/{id}` | Atualiza campos de um ticket |
| `GET` | `/tickets/{id}/comentarios` | Lista comentários de um ticket |

### Clientes

| Método | Endpoint | Descrição |
|---|---|---|
| `GET` | `/clientes` | Lista clientes |
| `GET` | `/clientes/{id}` | Retorna um cliente pelo ID |
| `GET` | `/clientes/{id}/tickets` | Lista tickets de um cliente |

---

## Formato de Payload

Todos os payloads são em **JSON** (`Content-Type: application/json`).

### Exemplo: criar ticket

```http
POST /tickets
Authorization: Bearer <token>
Content-Type: application/json

{
  "cliente_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "titulo": "Falha na sincronização com ERP",
  "descricao": "O processo de sync falha com timeout após 30 segundos.",
  "categoria": "integracao",
  "prioridade": "alta"
}
```

**Resposta `201 Created`:**

```json
{
  "id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
  "status": "aberto",
  "prazo_sla": "2026-10-12T10:00:00Z",
  "criado_em": "2026-10-10T10:00:00Z"
}
```

---

## Paginação

Todos os endpoints de listagem suportam paginação via query params:

| Param | Padrão | Máximo | Descrição |
|---|---|---|---|
| `page` | `1` | — | Número da página |
| `page_size` | `20` | `100` | Itens por página |

**Exemplo:**

```
GET /tickets?page=2&page_size=50&categoria=integracao&status=aberto
```

---

## Filtros Disponíveis em `/tickets`

| Param | Tipo | Exemplo |
|---|---|---|
| `status` | string | `aberto`, `resolvido` |
| `categoria` | string | `integracao`, `cobranca` |
| `prioridade` | string | `alta`, `critica` |
| `cliente_id` | UUID | `3fa85f64-...` |
| `agente_id` | UUID | `9b1deb4d-...` |
| `criado_apos` | ISO 8601 | `2026-10-01T00:00:00Z` |

---

## Versionamento

A API usa versionamento por prefixo de URL (`/v1`, `/v2`). A versão anterior (`/v1`) é mantida por **12 meses** após o lançamento de uma nova versão e depois desativada. Requisições à versão depreciada retornam o cabeçalho:

```
Sunset: Sat, 01 Aug 2026 00:00:00 GMT
Deprecation: true
```

---

## Códigos de Status

| Código | Significado |
|---|---|
| `200 OK` | Sucesso |
| `201 Created` | Recurso criado |
| `400 Bad Request` | Payload inválido ou campo obrigatório ausente |
| `401 Unauthorized` | Token ausente, inválido ou expirado |
| `403 Forbidden` | Token válido, mas sem permissão para o recurso |
| `404 Not Found` | Recurso não encontrado |
| `422 Unprocessable Entity` | Validação de negócio falhou |
| `429 Too Many Requests` | Limite de rate atingido — veja a Política de Rate Limiting |
| `500 Internal Server Error` | Erro interno — abra um ticket de suporte |

---

## Boas Práticas

- **Nunca** armazene `client_secret` em código-fonte ou repositórios. Use variáveis de ambiente ou cofres de segredo.
- Implemente **retry com backoff exponencial** para erros `5xx` e `429`.
- Sempre verifique o campo `expires_in` e renove o token com antecedência de pelo menos 60 segundos.
- Utilize o campo `categoria` nos tickets para garantir alinhamento com a base de conhecimento.
