# Configuração de MFA (Autenticação em Dois Fatores)

**Categoria:** acesso
**Tipo:** manual
**Versão:** 1.3
**Última atualização:** 2026-08-20

---

## O que é MFA

A Autenticação Multi-Fator (MFA) adiciona uma segunda camada de verificação ao login, exigindo que o usuário apresente algo que ele **sabe** (senha) e algo que ele **possui** (dispositivo com app autenticador). Mesmo que a senha seja comprometida, o acesso não autorizado é bloqueado sem o segundo fator.

---

## Aplicativos Suportados (TOTP)

A plataforma suporta qualquer app compatível com o padrão **TOTP (RFC 6238)**:

- Google Authenticator
- Microsoft Authenticator
- Authy
- 1Password (modo autenticador)
- Bitwarden Authenticator

---

## Ativando o MFA (Usuário)

1. Acesse **Perfil → Segurança → Autenticação em Dois Fatores**.
2. Clique em **Ativar MFA**.
3. Abra o app autenticador no celular e escaneie o QR Code exibido.
4. Digite o código de 6 dígitos gerado pelo app para confirmar a configuração.
5. **Salve os códigos de recuperação** exibidos — eles são mostrados apenas uma vez.

Após ativação, o segundo fator será solicitado a cada novo login.

---

## Códigos de Recuperação

Ao ativar o MFA, a plataforma gera **10 códigos de recuperação de uso único**. Use-os caso perca o acesso ao dispositivo autenticador.

- Cada código pode ser usado **apenas uma vez**.
- Após usar um código, ele é invalidado automaticamente.
- Se todos os códigos forem usados, gere novos em **Perfil → Segurança → Regenerar Códigos de Recuperação** (requer autenticação com MFA ativo).
- Armazene os códigos em local seguro (gerenciador de senhas, cofre físico) — nunca em e-mail ou mensagens.

---

## MFA Não Aceita o Código Gerado

Se o código TOTP está sendo recusado:

1. **Verifique o horário do dispositivo:** o TOTP é sensível a sincronização de tempo. Habilite a sincronização automática de hora no celular (Configurações → Data e Hora → Automático).
2. **Use o código antes de ele expirar:** cada código é válido por 30 segundos. Insira o código assim que ele aparecer no app.
3. **Confirme que está usando o app correto:** se você tem vários apps autenticadores, certifique-se de usar o que contém a entrada do Helpdesk.
4. **Tente o código seguinte:** aguarde o próximo código ser gerado (máx. 30 segundos) e tente novamente.

Se nenhuma dessas opções funcionar, use um **código de recuperação** para acessar a conta e reconfigurar o MFA.

---

## Desativação Emergencial pelo Administrador

Se um usuário perdeu o acesso ao dispositivo MFA e não possui códigos de recuperação:

1. Acesse **Configurações → Usuários e Permissões**.
2. Localize o usuário.
3. Clique em **Ações → Desativar MFA de Emergência**.
4. Confirme sua própria autenticação como administrador.
5. O MFA do usuário é desativado — **notifique o usuário** para reativá-lo imediatamente após o login.

> **Importante:** esta ação é registrada no log de auditoria. Use apenas em situações genuínas de perda de acesso.

---

## MFA Obrigatório para a Conta

Administradores podem exigir MFA para todos os usuários:

1. Acesse **Configurações → Segurança → Autenticação**.
2. Ative **MFA obrigatório para todos os usuários**.
3. Defina um **prazo de conformidade** (ex: 7 dias) — usuários têm até esse prazo para ativar antes de serem bloqueados.

Usuários sem MFA ativo após o prazo são redirecionados para a configuração no próximo login e não conseguem acessar outras áreas até concluir.
