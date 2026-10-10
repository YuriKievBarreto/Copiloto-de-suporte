# Redefinição de Senha — Guia do Administrador

**Categoria:** acesso
**Tipo:** manual
**Versão:** 2.1
**Última atualização:** 2026-09-10

---

## Visão Geral

Este guia descreve os procedimentos para redefinição de senha de usuários na plataforma Helpdesk Copilot, tanto pelo próprio usuário quanto pelo administrador da conta.

---

## Redefinição pelo Próprio Usuário

### Fluxo padrão

1. Na tela de login, clique em **Esqueci minha senha**.
2. Informe o e-mail cadastrado na conta.
3. Um e-mail com link de redefinição é enviado em até **2 minutos**.
4. O link tem validade de **30 minutos**. Após esse prazo, é necessário solicitar um novo.
5. Ao clicar no link, o usuário é direcionado para definir uma nova senha.

### Requisitos de complexidade da senha

| Critério | Requisito |
|---|---|
| Comprimento mínimo | 12 caracteres |
| Letras maiúsculas | Pelo menos 1 |
| Letras minúsculas | Pelo menos 1 |
| Números | Pelo menos 1 |
| Caracteres especiais | Pelo menos 1 (`!@#$%^&*`) |
| Senhas anteriores | Não pode reutilizar as últimas 5 senhas |

---

## Redefinição pelo Administrador

Administradores podem forçar a redefinição de senha de qualquer usuário da conta sem saber a senha atual.

### Passo a passo

1. Acesse **Configurações → Usuários e Permissões**.
2. Localize o usuário e clique em **Ações → Forçar Redefinição de Senha**.
3. Escolha entre:
   - **Enviar link por e-mail:** o usuário recebe um e-mail com o link de redefinição.
   - **Definir senha temporária:** o administrador define uma senha temporária que o usuário deverá alterar no primeiro login.
4. Confirme a ação.

> **Atenção:** ao usar a opção de senha temporária, o sistema invalida **todas as sessões ativas** do usuário imediatamente.

---

## E-mail de Redefinição Não Chegou

Se o usuário não receber o e-mail de redefinição:

1. Verifique a pasta de spam.
2. Confirme que o e-mail informado é o mesmo cadastrado na conta (não é possível redefinir para e-mails diferentes do cadastrado).
3. Verifique se a conta do usuário não foi **desativada** — usuários desativados não recebem e-mails da plataforma.
4. Aguarde até 5 minutos antes de solicitar um novo link — envios múltiplos em sequência podem ser bloqueados como spam.
5. Se o problema persistir, o administrador pode usar a opção de senha temporária como alternativa.

---

## Bloqueio por Tentativas Incorretas

Após **5 tentativas consecutivas** de login com senha incorreta, a conta é **bloqueada temporariamente por 30 minutos**. Após esse período, o bloqueio é removido automaticamente.

Se o usuário precisar de acesso imediato, o administrador pode desbloquear manualmente:

1. Acesse **Configurações → Usuários e Permissões**.
2. Localize o usuário (aparece com badge "Bloqueado").
3. Clique em **Ações → Desbloquear Conta**.

---

## Política de Expiração de Senha

Por padrão, senhas **não expiram**. Administradores podem habilitar expiração periódica:

1. Acesse **Configurações → Segurança → Política de Senhas**.
2. Ative **Expiração de senha** e configure o período (mínimo 30 dias).

Usuários com senha expirada são redirecionados para redefinição no próximo login.

---

## Integração com SSO

Se a conta usa **Single Sign-On (SSO)**, a senha da plataforma é gerenciada pelo provedor de identidade (IdP) externo e **não pode ser redefinida por este fluxo**. Redirecione o usuário para o processo de redefinição do IdP (Active Directory, Okta, Google Workspace, etc.).
