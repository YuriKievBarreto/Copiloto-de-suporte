variable "aws_region" {
  type        = string
  description = "Região da AWS para o API Gateway."
  default     = "us-east-1"
}

variable "project_name" {
  type        = string
  description = "Nome do projeto para identificação."
  default     = "copiloto-suport"
}

variable "environment" {
  type        = string
  description = "Ambiente."
  default     = "production"
}

variable "allowed_origins" {
  type        = list(string)
  description = "Origens permitidas para CORS (ex: seu GitHub Pages ou '*')."
  default     = ["*"]
}
