---
name: git-smart-commit
description: >-
  Analisa alterações pendentes no repositório Git, agrupa arquivos e hunks
  por finalidade lógica e cria commits atômicos e bem estruturados seguindo
  Conventional Commits. Use quando o usuário solicitar a criação de commits inteligentes,
  organização de alterações pendentes ou commits separados por propósito.
---

# Git Smart Commit

Esta skill orienta o agente a inspecionar alterações pendentes no repositório Git, agrupá-las por propósito lógico e criar commits atômicos, consistentes e seguros.

---

## 1. Fluxo de Trabalho Operacional

Execute o fluxo em 6 etapas estruturadas:

### Etapa 1: Inspecionar
1. Verifique o status geral e identifique alterações staged, unstaged e untracked:
   ```bash
   git status --short
   ```
2. Inspecione o histórico recente para identificar o padrão de mensagens e o idioma predominante:
   ```bash
   git log -n 5 --oneline
   ```
3. Examine o conteúdo detalhado das diferenças:
   ```bash
   git diff
   git diff --cached
   ```
4. Verifique arquivos não rastreados antes de considerar sua inclusão.

### Etapa 2: Agrupar
- Analise a intenção e a finalidade lógica de cada modificação.
- Agrupe arquivos e alterações que compartilham o mesmo objetivo (ex.: nova funcionalidade, correção de bug, atualização de documentação, refatoração).
- Arquivos de diretórios diferentes podem pertencer ao mesmo grupo se colaboram para a mesma finalidade.
- Não force a separação de arquivos ou mudanças interdependentes.

### Etapa 3: Planejar
Defina explicitamente a lista de grupos a serem commitados:
- Nome do grupo / Finalidade lógica.
- Arquivos ou hunks associados.
- Mensagem de commit planejada (no padrão Conventional Commits).
- Ordem lógica de commit (ex.: dependências e refatorações de suporte antes da funcionalidade principal).

### Etapa 4: Preparar
1. Adicione **apenas** os arquivos ou trechos pertencentes ao grupo da vez:
   ```bash
   git add <caminho/do/arquivo1> <caminho/do/arquivo2>
   ```
2. Para arquivos com múltiplas alterações não relacionadas, faça o staging granular por hunks (ex.: via patch interativo ou preparando seletivamente).
3. Valide o staging antes de commitar:
   ```bash
   git diff --cached
   ```

### Etapa 5: Commitar
1. Crie o commit para o grupo atual com mensagem clara e descritiva:
   ```bash
   git commit -m "<mensagem de commit>"
   ```
2. Repita as etapas 4 e 5 para os próximos grupos planejados.

### Etapa 6: Verificar
1. Confirme os commits criados no log:
   ```bash
   git log -n <qtd_commits_criados> --stat
   ```
2. Verifique o estado final do repositório para conferir o que restou:
   ```bash
   git status
   ```

---

## 2. Convenção de Commits

Utilize **Conventional Commits**:
```text
<tipo>(<escopo>): <descrição>
```
*O `<escopo>` é opcional e deve representar o módulo, serviço ou componente afetado.*

### Tipos Permitidos
- `feat`: Nova funcionalidade ou recurso para o usuário/sistema.
- `fix`: Correção de bug ou comportamento inesperado.
- `refactor`: Alteração de código que não corrige bug nem adiciona funcionalidade.
- `test`: Adição ou correção de testes automatizados.
- `docs`: Modificações exclusivamente em documentação (ex.: README, guias).
- `chore`: Atualizações de tarefas de build, pacotes, dependências ou ferramentas de suporte.
- `perf`: Mudança de código voltada para melhoria de desempenho.
- `ci`: Alterações em pipelines e configurações de CI/CD.

### Idioma e Estilo
- Respeite o idioma predominante no histórico recente (`git log`).
- Se o projeto utiliza português no histórico, escreva mensagens em português.
- Na ausência de padrão identificado, utilize inglês conciso e imperativo.

---

## 3. Regras de Agrupamento Lógico

- **Finalidade única:** Cada commit deve representar uma unidade coesa de trabalho.
- **Atomicidade sem quebra:** Não separe mudanças interdependentes que deixariam a aplicação ou os testes quebrados em commits intermediários.
- **Granularidade equilibrada:** Evite extremos:
  - Não crie commits microscópicos para cada linha modificada.
  - Não agrupe em um único commit alterações não relacionadas entre si.
- **Fidelidade ao código:** Não deduza ou invente finalidades que não estejam comprovadas pelas alterações reais.

---

## 4. Segurança e Preservação do Repositório

> [!CAUTION]
> A preservação do trabalho existente e a proteção de segredos são prioridades absolutas.

- **Preservação de Staging Preexistente:** Se o repositório já continha alterações staged antes do início do fluxo, analise-as. Não as misture inadvertidamente com novos grupos. Caso não seja possível preservar com segurança o staging preexistente, interrompa a execução antes de modificar o estado do Git e explique o cenário ao usuário.
- **Proibido Comandos Destrutivos:** NUNCA execute `git reset --hard`, `git checkout` para descartar mudanças, nem `git restore` com finalidade destrutiva.
- **Staging Controlado:** NUNCA utilize `git add .` ou `git add -A` sem filtragem prévia. Sempre adicione arquivos explicitamente.
- **Proteção contra Vazamento de Segredos:** NUNCA inclua arquivos `.env`, chaves privadas, certificados, credenciais ou tokens em commits. Verifique arquivos não rastreados antes do staging.
- **Imutabilidade do Histórico:** NUNCA use `git commit --amend`, rebase, squash ou reescrita de histórico durante este fluxo.
- **Sem Push Automático:** NUNCA execute `git push` automaticamente sem instrução explícita do usuário.
- **Respeito aos Hooks:** NUNCA use flags como `--no-verify` para forçar commits ignorando validações configuradas.
- **Intocabilidade do Código:** NUNCA modifique ou reformate arquivos de código-fonte exclusivamente para facilitar o agrupamento.

---

## 5. Autonomia e Tomada de Decisão

- **Execução Autônoma:** Quando o usuário solicitar a criação dos commits, execute o fluxo completo de forma autônoma sem pedir confirmação a cada grupo, desde que as alterações sejam bem compreensíveis e a separação seja segura.
- **Pontos de Interrupção Obrigatórios:** Interrompa a operação e consulte o usuário se:
  - Houver risco de perda ou sobreposição de alterações.
  - Houver arquivos com alterações conflitantes ou ambíguas cujo propósito seja incerto.
  - O staging preexistente não puder ser distinguido com certeza das novas modificações.
  - Forem encontrados possíveis segredos ou credenciais em arquivos pendentes.

---

## 6. Resultado Esperado

Ao concluir a execução, apresente um resumo objetivo contendo:

1. **Commits Criados:** Hash curto e mensagem de cada commit gerado.
2. **Arquivos por Commit:** Lista de arquivos incluídos em cada commit.
3. **Testes e Validações:** Testes ou verificações executados (se houver) e seus respectivos resultados.
4. **Pendências:** Lista de alterações que permaneceram unstaged ou não rastreadas.
5. **Estado Final:** Saída resumida do `git status`.

> [!NOTE]
> Nunca afirme que um commit, verificação ou teste foi bem-sucedido sem checar a saída real dos comandos.
