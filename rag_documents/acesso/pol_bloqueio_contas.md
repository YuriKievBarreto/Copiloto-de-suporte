# Política de Bloqueio e Desbloqueio de Contas

**Categoria:** acesso
**Tipo:** politica
**Versão:** 1.4
**Última atualização:** 2026-08-30

---

## Objetivo

Esta política define as condições que levam ao bloqueio automático ou manual de contas de usuário, os procedimentos para desbloqueio e as responsabilidades envolvidas.

---

## Gatilhos de Bloqueio Automático

### 1. Tentativas de login incorretas

| Situação | Comportamento |
|---|---|
| 5 tentativas consecutivas com senha errada | Bloqueio temporário de **30 minutos** |
| 10 tentativas dentro de 1 hora | Bloqueio por **2 horas** |
| 20 tentativas dentro de 24 horas | Bloqueio permanente (requer intervenção do administrador) |

O contador de tentativas é resetado após um login bem-sucedido ou após o período de bloqueio.

### 2. Inatividade prolongada

Contas sem login por mais de **90 dias** são automaticamente **desativadas** (não bloqueadas — o usuário não aparece como bloqueado, mas não consegue fazer login). O administrador recebe notificação 7 dias antes da desativação.

### 3. Solicitação administrativa

Administradores podem bloquear uma conta manualmente por razões de segurança (ex: colaborador desligado, suspeita de comprometimento de credenciais).

### 4. Detecção de atividade suspeita

O sistema pode bloquear preventivamente uma conta caso detecte:
- Login de localização geográfica muito diferente da habitual em curto intervalo.
- Tentativa de acesso com credenciais de um IP listado em bases de ameaças conhecidas.
- Volume anormal de requisições à API em curto período.

---

## Tipos de Bloqueio

| Tipo | Duração | Desbloqueio |
|---|---|---|
| **Temporário automático** | 30 min a 2 horas | Automático após o período |
| **Permanente por tentativas** | Indefinido | Apenas pelo administrador |
| **Desativação por inatividade** | Indefinido | Apenas pelo administrador |
| **Bloqueio administrativo** | Indefinido | Apenas pelo administrador |
| **Bloqueio por atividade suspeita** | Indefinido | Pelo administrador após verificação |

---

## Fluxo de Desbloqueio

### Desbloqueio pelo administrador

1. Acesse **Configurações → Usuários e Permissões**.
2. Localize o usuário — contas bloqueadas aparecem com badge laranja ou vermelho.
3. Clique em **Ações** e escolha a ação adequada:
   - **Desbloquear:** remove o bloqueio e mantém a senha atual.
   - **Desbloquear e forçar redefinição de senha:** recomendado em casos de suspeita de comprometimento.
   - **Reativar conta:** para contas desativadas por inatividade.
4. Confirme sua autenticação de administrador.
5. O sistema registra a ação no **log de auditoria** com timestamp e identificação do administrador.

### Papéis autorizados a desbloquear

| Papel | Pode desbloquear |
|---|---|
| Administrador da conta | ✅ Qualquer usuário |
| Agente sênior | ✅ Agentes com nível inferior |
| Agente pleno/junior | ❌ Não autorizado |
| O próprio usuário bloqueado | ❌ Não autorizado (exceto bloqueio temporário automático) |

---

## Notificações

| Evento | Quem é notificado |
|---|---|
| Conta bloqueada por tentativas | Usuário (e-mail) + Administrador |
| Conta bloqueada por atividade suspeita | Administrador apenas |
| Conta prestes a ser desativada por inatividade | Usuário (7 dias antes) + Administrador |
| Conta desbloqueada | Usuário (e-mail) |

---

## Boas Práticas de Segurança

- Bloqueie imediatamente contas de colaboradores desligados da empresa — não espere o processo automático de inatividade.
- Em caso de suspeita de comprometimento, além de bloquear a conta, revogue os tokens de API associados em **Configurações → Integrações → Credenciais**.
- Ative MFA obrigatório para reduzir o risco de bloqueios por tentativas de força bruta.
- Revise periodicamente as contas inativas — contas não utilizadas representam superfície de ataque desnecessária.
