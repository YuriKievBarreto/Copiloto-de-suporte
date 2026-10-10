# Exportação de Relatórios e Auditoria

**Categoria:** outro
**Tipo:** manual
**Versão:** 1.2
**Última atualização:** 2026-09-12

---

## Visão Geral

A plataforma oferece duas funcionalidades distintas de exportação de dados:

1. **Relatórios operacionais:** exportação de dados de tickets, SLA e desempenho de agentes para análise externa.
2. **Log de auditoria:** registro imutável de ações administrativas e de segurança, exportável para conformidade.

---

## Relatórios Operacionais

### Acesso

Disponível em **Relatórios → Exportar** para usuários com perfil **Gerente** ou **Administrador**.

### Formatos Disponíveis

| Formato | Uso recomendado |
|---|---|
| CSV | Planilhas, scripts de análise, ferramentas de BI |
| JSON | Integrações com sistemas externos, APIs |
| XLSX | Excel, LibreOffice Calc |

### Relatórios Disponíveis

| Relatório | Conteúdo |
|---|---|
| **Tickets** | Todos os campos de tickets com filtros por período, categoria, status e agente |
| **SLA** | Tickets com prazo_sla, resolvido_em, status de cumprimento (dentro/fora do prazo) |
| **Desempenho de agentes** | Volume de tickets por agente, tempo médio de resolução, taxa de SLA cumprido |
| **Clientes** | Dados de clientes com volume de tickets e distribuição por categoria |
| **Comentários** | Histórico de interações (apenas comentários públicos por padrão) |

### Limites por Plano

| Plano | Linhas por exportação | Exportações simultâneas | Período máximo |
|---|---|---|---|
| Free | 500 | 1 | 30 dias |
| Pro | 50.000 | 3 | 12 meses |
| Enterprise | Ilimitado | 10 | Sem limite |

Exportações acima de 10.000 linhas são processadas em background — você recebe um e-mail com o link para download quando o arquivo estiver pronto (validade do link: 48 horas).

---

## Upload de Arquivo Falha

Se o upload de arquivo no módulo de relatórios (ou em outras áreas da plataforma) falhar:

**Limites de tamanho:**
- Arquivos de até **5 MB** são processados diretamente no browser.
- Arquivos entre 5 MB e 100 MB usam upload em partes (multipart) — certifique-se de que sua rede não interrompe conexões longas.
- Arquivos acima de **100 MB** não são suportados — comprima ou divida antes de enviar.

**Formatos aceitos para upload:** PDF, PNG, JPG, CSV, XLSX, ZIP (máx. 100 MB comprimido).

Se o upload falhar dentro do limite de 5 MB:
1. Verifique se o formato do arquivo é suportado.
2. Tente em outro navegador (Chrome ou Firefox recomendados).
3. Desative extensões de bloqueio de conteúdo.
4. Se persistir, abra um ticket com categoria `outro` incluindo o erro exibido.

---

## Agendamento de Relatórios

Planos Pro e Enterprise podem agendar exportações automáticas:

1. Em **Relatórios → Exportar**, configure os filtros desejados.
2. Clique em **Agendar**.
3. Defina a frequência (diária, semanal, mensal) e o horário.
4. Informe o e-mail de destino para receber o arquivo.

---

## Log de Auditoria

### O que é registrado

O log de auditoria captura automaticamente:

| Categoria | Exemplos |
|---|---|
| **Acesso** | Login, logout, tentativas falhas, desbloqueio de conta |
| **Permissões** | Alteração de perfil de usuário, criação/remoção de usuário |
| **Configuração** | Alterações em SSO, MFA, webhooks, integrações |
| **Dados** | Exportações realizadas, tickets deletados, alterações em massa |
| **Segurança** | Ativação/desativação de MFA, reset de senha forçado |

### Retenção

| Plano | Retenção do log |
|---|---|
| Free | 30 dias |
| Pro | 12 meses |
| Enterprise | 5 anos |

### Exportação do Log de Auditoria

1. Acesse **Configurações → Auditoria → Exportar Log**.
2. Filtre por período, usuário ou categoria de evento.
3. Exporte em formato JSON ou CSV.

O log de auditoria é **imutável** — nenhum usuário, incluindo administradores, pode editar ou deletar entradas. Isso garante a integridade para fins de conformidade (LGPD, ISO 27001, SOC 2).
