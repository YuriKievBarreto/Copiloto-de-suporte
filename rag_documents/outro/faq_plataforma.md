# Perguntas Frequentes — Plataforma Geral

**Categoria:** outro
**Tipo:** faq
**Versão:** 1.8
**Última atualização:** 2026-10-01

---

## Dashboard

**O dashboard não carrega os gráficos. O que fazer?**

Verifique as seguintes causas comuns:

1. **Extensões do navegador:** bloqueadores de anúncio e scripts (uBlock Origin, AdBlock) podem interferir no carregamento dos gráficos. Tente em uma aba anônima ou com extensões desativadas.
2. **Cache desatualizado:** pressione `Ctrl + Shift + R` (Windows) ou `Cmd + Shift + R` (Mac) para forçar recarregamento sem cache.
3. **Navegador desatualizado:** certifique-se de estar usando uma versão recente de Chrome, Firefox ou Edge.
4. **Filtros aplicados sem dados:** se nenhum dado corresponde ao filtro ativo (ex: período sem tickets), o gráfico aparece vazio mas não é um erro. Ajuste os filtros.

Se nenhuma das opções resolver, abra um ticket com a categoria `outro`, incluindo o nome do gráfico afetado e uma captura de tela do console do browser (F12 → Console).

---

**O dashboard está mostrando dados desatualizados. Com que frequência os dados são atualizados?**

Os dados do dashboard são atualizados em **tempo real** para métricas operacionais (contagem de tickets abertos, tickets críticos) e **a cada 5 minutos** para métricas analíticas (tempo médio de resolução, taxa de SLA). Se os dados parecerem desatualizados além desses intervalos, force uma atualização clicando no ícone de refresh no painel ou recarregue a página.

---

## Relatórios

**O relatório exportado está chegando vazio ou com menos linhas do que o esperado.**

Possíveis causas:
1. **Filtros muito restritivos:** revise os filtros de data, categoria e status aplicados antes da exportação.
2. **Limite do plano:** planos Free exportam no máximo 500 linhas. Se você tem mais dados, considere fazer a exportação em partes por período.
3. **Exportação em processamento:** exportações grandes são processadas em background. Aguarde o e-mail com o link de download.

---

## Notificações

**As notificações por e-mail pararam de chegar. Como resolver?**

1. Verifique se o e-mail configurado está correto em **Perfil → Notificações**.
2. Confira a pasta de spam — filtros agressivos podem reter e-mails transacionais.
3. Verifique se as notificações não foram desativadas em **Perfil → Notificações → Preferências**.
4. Verifique se o domínio `@helpdesk.interno` está na lista de remetentes confiáveis do seu cliente de e-mail.
5. Se sua empresa usa filtros de e-mail corporativos, solicite ao TI que libere os domínios de envio da plataforma.

---

**Estou recebendo notificações demais. Como filtrar?**

Acesse **Perfil → Notificações → Preferências** e configure quais eventos geram notificação:

- Ticket atribuído a mim
- Comentário adicionado ao meu ticket
- SLA próximo do vencimento
- Ticket escalado para mim
- Atualizações de tickets que sigo

Você pode optar por receber **notificações em tempo real** (e-mail imediato) ou **resumo diário** (um e-mail consolidado ao fim do dia).

---

## Performance

**A plataforma está muito lenta no período noturno. É normal?**

Não. A plataforma opera com performance consistente 24/7. Lentidão no período noturno geralmente indica um dos cenários abaixo:

1. **Job de manutenção em execução:** verificar o status em **Status → Manutenção Programada**.
2. **Problema de rede local:** teste acessando de outra rede ou dispositivo.
3. **Incidente de infraestrutura:** consulte a página de status da plataforma.

Consulte também o **Caso Resolvido: Degradação de Performance no Período Noturno** para um exemplo de investigação e solução desse tipo de problema. Se o problema persistir, abra um ticket com categoria `outro` incluindo o horário e a duração da lentidão.

---

## Upload de Arquivos

**O upload de arquivo falha sem mensagem de erro clara.**

Limite de tamanho por plano:
- **Free / Pro:** até 5 MB por arquivo
- **Enterprise:** até 100 MB por arquivo

Arquivos acima do limite são rejeitados silenciosamente em alguns navegadores. Comprima o arquivo ou divida em partes menores. Formatos suportados: PDF, PNG, JPG, CSV, XLSX, ZIP. Outros formatos são bloqueados por segurança.

---

## Módulo de Auditoria

**O módulo de auditoria não está registrando algumas ações. Como verificar?**

O log de auditoria registra automaticamente ações administrativas e de segurança — não registra ações operacionais rotineiras de agentes (ex: visualizar um ticket). Se uma ação específica deveria ser registrada e não está, verifique:

1. Se você tem o perfil **Administrador** para acessar o log completo (agentes veem apenas suas próprias ações).
2. Se está filtrando pelo período correto.
3. Se a categoria da ação está selecionada no filtro.

Consulte o Manual de Exportação de Relatórios e Auditoria para a lista completa de eventos registrados.
