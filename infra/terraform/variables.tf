variable "aws_region" {
  type        = string
  description = "Região da AWS para provisionamento dos recursos."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Nome do projeto para identificação e tags."
  default     = "copiloto-suport"
}

variable "environment" {
  type        = string
  description = "Ambiente de implantação."
  default     = "production"
}

variable "instance_type" {
  type        = string
  description = "Tipo da instância EC2 Spot."
  default     = "t3.micro"
}

variable "root_volume_size" {
  type        = number
  description = "Tamanho do disco root em GB (EBS gp3)."
  default     = 20

  validation {
    condition     = var.root_volume_size >= 8 && var.root_volume_size <= 100
    error_message = "O tamanho do volume deve estar entre 8 e 100 GB."
  }
}

variable "spot_max_price" {
  type        = string
  description = "Preço máximo por hora para a instância Spot (null = teto On-Demand padrão da AWS)."
  default     = null
}

variable "ssh_allowed_cidr" {
  type        = string
  description = "Bloco CIDR IPv4 com permissão permanente de acesso SSH na porta 22 (opcional, ex.: 'SEU_IP/32'). Se nulo, o acesso SSH fica fechado por padrão e aberto apenas temporariamente via CI/CD."
  default     = null

  validation {
    condition     = var.ssh_allowed_cidr == null || can(cidrhost(var.ssh_allowed_cidr, 0))
    error_message = "O valor informado em ssh_allowed_cidr deve ser nulo ou um CIDR IPv4 válido (ex.: 203.0.113.10/32)."
  }
}

variable "ssh_public_key" {
  type        = string
  description = "Conteúdo direto da chave pública SSH (útil para injeção via GitHub Actions secrets/vars)."
  default     = null
}

variable "api_allowed_cidr" {
  type        = string
  description = "Bloco CIDR com permissão para acessar a porta da API."
  default     = "0.0.0.0/0"

  validation {
    condition     = can(cidrhost(var.api_allowed_cidr, 0))
    error_message = "O valor informado em api_allowed_cidr deve ser um CIDR IPv4 válido."
  }
}

variable "api_port" {
  type        = number
  description = "Porta TCP exposta pela API FastAPI."
  default     = 8000
}

variable "existing_key_name" {
  type        = string
  description = "Nome de um EC2 Key Pair já existente na conta AWS. Se informado, substitui ssh_public_key_path."
  default     = null
}

variable "ssh_public_key_path" {
  type        = string
  description = "Caminho da chave pública SSH local para criação de novo Key Pair (ex.: '~/.ssh/id_ed25519.pub')."
  default     = null
}

variable "subnet_id" {
  type        = string
  description = "ID de uma subnet pública da Default VPC. Se omitido (null), a AWS aloca na subnet padrão com capacidade Spot."
  default     = null
}
