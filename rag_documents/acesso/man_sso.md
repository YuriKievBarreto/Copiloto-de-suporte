# Configuração de SSO (Single Sign-On)

**Categoria:** acesso
**Tipo:** manual
**Versão:** 1.5
**Última atualização:** 2026-09-05

---

## O que é SSO

O Single Sign-On (SSO) permite que usuários acessem a plataforma Helpdesk Copilot com as credenciais corporativas do provedor de identidade (IdP) da empresa, sem precisar de uma senha separada. O login é feito uma única vez no IdP e o acesso à plataforma é concedido automaticamente.

---

## Provedores Suportados

| Provedor | Protocolo | Status |
|---|---|---|
| Microsoft Azure AD / Entra ID | SAML 2.0 | ✅ Suportado |
| Google Workspace | SAML 2.0 | ✅ Suportado |
| Okta | SAML 2.0 | ✅ Suportado |
| Auth0 | SAML 2.0 / OIDC | ✅ Suportado |
| Active Directory (ADFS) | SAML 2.0 | ✅ Suportado |
| Outros provedores SAML 2.0 | SAML 2.0 | ✅ Compatível |

> SSO está disponível apenas para planos **Pro** e **Enterprise**.

---

## Configuração (SAML 2.0)

### Passo 1 — Obter metadados da plataforma

1. Acesse **Configurações → Segurança → Single Sign-On**.
2. Copie as seguintes informações para configurar no IdP:
   - **Entity ID (Issuer):** `https://auth.helpdesk.interno/saml/metadata`
   - **ACS URL (Assertion Consumer Service):** `https://auth.helpdesk.interno/saml/acs`
   - **Metadados XML:** disponível para download

### Passo 2 — Configurar no IdP

No painel do seu provedor de identidade, crie uma nova aplicação SAML com os dados obtidos no passo 1. Configure os **atributos mapeados** conforme a tabela abaixo.

### Passo 3 — Importar metadados do IdP

1. Baixe o arquivo de metadados XML do seu IdP (ou copie a URL de metadados).
2. Em **Configurações → Segurança → SSO**, cole a URL ou faça upload do arquivo XML.
3. Clique em **Salvar e Testar Conexão**.

---

## Atributos SAML Mapeados

| Atributo SAML (enviado pelo IdP) | Campo na plataforma | Obrigatório |
|---|---|---|
| `email` | E-mail do usuário | ✅ Sim |
| `given_name` | Primeiro nome | ✅ Sim |
| `family_name` | Sobrenome | ❌ Opcional |
| `groups` | Grupos/perfis do usuário | ❌ Opcional |
| `department` | Departamento | ❌ Opcional |

O atributo `email` é o identificador principal — usuários são associados pela combinação domínio + e-mail.

---

## Provisionamento de Usuários

Por padrão, usuários que fazem login via SSO pela primeira vez são criados automaticamente na plataforma com perfil **Básico**. O administrador pode alterar o perfil após o primeiro acesso.

Para desabilitar a criação automática (apenas usuários pré-cadastrados podem logar):

1. Acesse **Configurações → SSO → Provisionamento**.
2. Desative **Criar usuário automaticamente no primeiro login**.

---

## Troubleshooting

### "Erro de configuração SSO" ao fazer login

Verifique:
1. Se a **ACS URL** cadastrada no IdP corresponde exatamente à URL da plataforma (sem barra no final, sem espaços).
2. Se o **Entity ID** está igual nos dois lados.
3. Se o certificado do IdP não está expirado — baixe os metadados atualizados do IdP e reimporte.
4. Se o atributo `email` está sendo enviado corretamente pelo IdP — use a ferramenta **SAML Tracer** no browser para inspecionar o token.

### Usuário redirecionado para o login mas não consegue entrar

- Confirme que o e-mail do usuário no IdP é o mesmo cadastrado na plataforma.
- Verifique se o usuário está ativo no IdP (não suspenso ou desativado).
- Verifique se o usuário está no grupo/aplicação correto no IdP que tem acesso à plataforma.

### SSO funciona para alguns usuários mas não para outros

Provavelmente um problema de atribuição no IdP. Confirme que todos os usuários afetados estão atribuídos à aplicação SAML no painel do IdP.

---

## Desativação do SSO

Para desativar o SSO e voltar ao login com senha:

1. Acesse **Configurações → Segurança → SSO**.
2. Clique em **Desativar SSO**.
3. Os usuários receberão e-mail para definir uma senha individual.

> **Atenção:** se MFA estava sendo gerenciado pelo IdP, os usuários precisarão configurar MFA diretamente na plataforma após a desativação do SSO.
