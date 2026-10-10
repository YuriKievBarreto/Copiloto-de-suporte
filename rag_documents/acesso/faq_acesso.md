# Perguntas Frequentes — Acesso e Autenticação

**Categoria:** acesso
**Tipo:** faq
**Versão:** 2.1
**Última atualização:** 2026-10-01

---

## Senha

**Esqueci minha senha. Como faço para recuperar?**

Na tela de login, clique em **Esqueci minha senha** e informe o e-mail cadastrado. Um link de redefinição é enviado em até 2 minutos e tem validade de 30 minutos. Se não receber o e-mail, verifique a pasta de spam. Se usar SSO, a senha é gerenciada pelo seu provedor de identidade — contate o TI da sua empresa. Consulte o Manual de Redefinição de Senha para o passo a passo completo.

---

**Estou tentando redefinir a senha mas o link diz que expirou. O que fazer?**

Links de redefinição expiram em 30 minutos. Retorne à tela de login, clique em **Esqueci minha senha** novamente e solicite um novo link. Se a conta estiver bloqueada, o link não funcionará até que o bloqueio seja removido pelo administrador.

---

## MFA

**O código de autenticação (MFA) não está sendo aceito. O que fazer?**

O código TOTP é válido por apenas 30 segundos e depende do horário exato do dispositivo. Verifique:
1. Se a sincronização automática de hora está ativada no celular.
2. Se está usando o app e a conta corretos no autenticador.
3. Aguarde o próximo código ser gerado e tente novamente.

Se o problema persistir, use um **código de recuperação** (gerado quando você ativou o MFA). Consulte o Manual de MFA para mais detalhes.

---

**Perdi o celular com o app autenticador e não tenho os códigos de recuperação. O que fazer?**

Entre em contato com o administrador da sua conta. Ele pode desativar emergencialmente o MFA em **Configurações → Usuários → Desativar MFA de Emergência**. Após o login, reative o MFA imediatamente em um novo dispositivo.

---

**Recebi um e-mail de convite para criar conta mas o link não funciona.**

Links de convite expiram em **72 horas**. Solicite ao administrador da conta que reenvie o convite em **Configurações → Usuários → Reenviar Convite**. Se o link estiver dentro do prazo mas ainda não funcionar, tente abrir em uma aba anônima ou em outro navegador.

---

## Sessão

**Minha sessão expira muito rápido (menos de 1 minuto). É normal?**

Não. A duração padrão de sessão é de **8 horas** para usuários ativos. Sessões muito curtas geralmente indicam:
- Diferença de horário entre o servidor e o navegador (problema de fuso horário).
- Extensão do navegador invalidando cookies de sessão.
- Política de segurança corporativa via proxy que força logout.

Tente desativar extensões do navegador e acessar diretamente sem proxy. Se o problema persistir, abra um ticket com categoria `acesso`.

---

## Permissões

**Minhas permissões de administrador foram removidas sem que eu tenha solicitado. O que aconteceu?**

Possíveis causas:
1. Outro administrador alterou seu perfil — verifique o log de auditoria em **Configurações → Auditoria**.
2. Migração de conta que resetou perfis para o padrão.
3. Alteração de política de permissões por SSO (se sua conta usa SSO, o grupo no IdP pode ter mudado).

Solicite ao administrador principal que verifique e restaure as permissões. Se for o único administrador da conta, abra um ticket com categoria `acesso` e prioridade `alta`.

---

## Conta Bloqueada

**Minha conta foi bloqueada. Como desbloquear?**

Bloqueios temporários (até 2 horas) são removidos automaticamente. Para bloqueios permanentes, entre em contato com o administrador da sua conta. Ele pode desbloquear em **Configurações → Usuários → Desbloquear Conta**. Consulte a Política de Bloqueio e Desbloqueio de Contas para entender os gatilhos e o fluxo completo.

---

## SSO

**O SSO está retornando um erro de configuração ao fazer login. O que verificar?**

Erros de SSO geralmente são causados por:
- Certificado do provedor de identidade expirado.
- URL de retorno (ACS URL) incorreta na configuração do IdP.
- Atributo de e-mail não sendo enviado pelo IdP no token SAML.

Consulte o Manual de Configuração de SSO para o checklist completo de troubleshooting. Se não resolver, abra um ticket com categoria `acesso` e inclua o ID de correlação do erro (exibido na tela de erro do SSO).
