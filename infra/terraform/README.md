# Infraestrutura e Pipeline de Deploy (Copiloto de Suporte)

Este diretório contém os manifestos Terraform e configurações para provisionamento de infraestrutura na AWS e automação CI/CD via GitHub Actions.

---

## 🏗️ Arquitetura

- **EC2 Spot AL2023 (`t3.micro`)**: Hospeda a aplicação FastAPI em container Docker.
- **IAM Role & Instance Profile (`copiloto-suport-production-ec2-role`)**: Permissões mínimas para AWS Bedrock (`InvokeModel` e `InvokeModelWithResponseStream` no modelo `us.amazon.nova-2-lite-v1:0` e Titan Embeddings v2).
- **IMDSv2 Hop Limit 2**: Permite que o container Docker na rede bridge consulte credenciais IAM da EC2 sem chaves AWS estáticas no `.env`.
- **Security Group**:
  - Porta 8000 aberta para a internet (`0.0.0.0/0`).
  - Porta 22 (SSH) fechada por padrão ou restrita via `ssh_allowed_cidr` (o GitHub Actions abre temporariamente apenas para o IP do runner e revoga ao término).
- **Terraform Backend Remoto S3 com Native Locking**:
  - Utiliza `use_lockfile = true` (Terraform >= 1.10), dispensando tabela DynamoDB separada.

---

## 🔑 Configuração dos Secrets no GitHub Actions

Acesse o repositório no GitHub: **Settings > Secrets and variables > Actions** e adicione os seguintes secrets:

| Secret | Obrigatório? | Descrição / Exemplo |
| :--- | :---: | :--- |
| `AWS_ACCESS_KEY_ID` | **Sim** | Access Key do usuário IAM com permissão para provisionar EC2/IAM/SG. |
| `AWS_SECRET_ACCESS_KEY` | **Sim** | Secret Key da AWS correspondente. |
| `AWS_REGION` | Não | Região da AWS (padrão: `us-east-1`). |
| `TF_STATE_BUCKET` | **Sim** | Nome do bucket S3 criado para armazenar o estado do Terraform. |
| `EC2_SSH_PRIVATE_KEY` | **Sim** | Conteúdo da chave privada SSH (formato PEM / OpenSSH) usada para conectar à EC2. |
| `TF_VAR_EXISTING_KEY_NAME` | Condicional* | Nome do Key Pair já cadastrado na AWS (ex.: `copiloto-suport-production-key`). |
| `TF_VAR_SSH_PUBLIC_KEY` | Condicional* | Chave pública SSH caso queira que o Terraform registre um novo Key Pair. |
| `POSTGRES_CONN_STRING` | **Sim** | URL de conexão PostgreSQL Neon (`postgresql://...`). |
| `CLUSTER_ENDPOINT` | **Sim** | Endpoint da nuvem Qdrant (`https://...`). |
| `QDRANT_API_KEY` | **Sim** | API Key do cluster Qdrant Cloud. |
| `LANGCHAIN_TRACING_V2` | Não | `"true"` ou `"false"` para rastreamento LangSmith. |
| `LANGCHAIN_API_KEY` | Não | Chave de API do LangSmith. |
| `LANGCHAIN_PROJECT` | Não | Nome do projeto no LangSmith (padrão: `copiloto-suport`). |

*\*Informe `TF_VAR_EXISTING_KEY_NAME` se já criou o Key Pair na AWS, OU `TF_VAR_SSH_PUBLIC_KEY` para o Terraform criá-lo.*

---

## 📦 Migração do Estado Local para o S3 (Executar uma única vez)

Como você já aplicou o Terraform localmente, execute os comandos abaixo para migrar o arquivo `terraform.tfstate` para o bucket S3:

1. **Crie o bucket S3 (se ainda não existir):**
   ```bash
   aws s3api create-bucket --bucket SEU_NOME_DE_BUCKET_TFSTATE --region us-east-1
   aws s3api put-bucket-versioning --bucket SEU_NOME_DE_BUCKET_TFSTATE --versioning-configuration Status=Enabled
   aws s3api put-bucket-encryption --bucket SEU_NOME_DE_BUCKET_TFSTATE --server-side-encryption-configuration '{"Rules": [{"ApplyServerSideEncryptionByDefault": {"SSEAlgorithm": "AES256"}}]}'
   ```

2. **Migre o estado existente:**
   ```bash
   cd infra/terraform
   terraform init -backend-config="bucket=SEU_NOME_DE_BUCKET_TFSTATE" -migrate-state
   ```
   *(Responda `yes` quando o Terraform solicitar a migração dos recursos).*

---

## 🚀 Workflows Disponíveis

1. **Deploy (`.github/workflows/deploy.yml`):**
   - Disparado automaticamente em qualquer `push` na branch `main` ou manualmente via `workflow_dispatch`.
   - Executa a suíte de testes (`pytest`).
   - Inicializa e aplica o Terraform.
   - Libera temporariamente a porta 22 para o IP do runner do GitHub.
   - Conecta via SSH, clona/atualiza o repositório no commit exato, compila a imagem Docker e sobe o container.
   - Executa verificação de saúde local e remota (`GET /health`).
   - Revoga a regra de SSH temporária no Security Group.

2. **Destroy (`.github/workflows/destroy.yml`):**
   - Disparo manual exclusivo via `workflow_dispatch`.
   - Requer confirmação digitando explicitamente `DESTROY`.
   - Destrói todos os recursos provisionados na AWS (EC2, Security Group, IAM Role, Key Pair).
