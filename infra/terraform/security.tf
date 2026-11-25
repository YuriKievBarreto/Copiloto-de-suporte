locals {
  resolved_ssh_public_key = var.ssh_public_key != null ? trimspace(var.ssh_public_key) : (
    var.ssh_public_key_path != null ? trimspace(file(pathexpand(var.ssh_public_key_path))) : null
  )
}

data "aws_vpc" "default" {
  default = true
}

resource "aws_security_group" "api" {
  name        = "${var.project_name}-${var.environment}-sg"
  description = "Security Group para API e acesso SSH restrito"
  vpc_id      = data.aws_vpc.default.id

  tags = {
    Name = "${var.project_name}-${var.environment}-sg"
  }
}

resource "aws_vpc_security_group_ingress_rule" "ssh" {
  count             = var.ssh_allowed_cidr != null ? 1 : 0
  security_group_id = aws_security_group.api.id
  description       = "Acesso SSH restrito ao IP do administrador"
  cidr_ipv4         = var.ssh_allowed_cidr
  from_port         = 22
  ip_protocol       = "tcp"
  to_port           = 22
}

resource "aws_vpc_security_group_ingress_rule" "api" {
  security_group_id = aws_security_group.api.id
  description       = "Trafego de entrada para a API FastAPI"
  cidr_ipv4         = var.api_allowed_cidr
  from_port         = var.api_port
  ip_protocol       = "tcp"
  to_port           = var.api_port
}

resource "aws_vpc_security_group_egress_rule" "all_outbound" {
  security_group_id = aws_security_group.api.id
  description       = "Permite trafego de saida para internet (Bedrock, Neon, Qdrant e pacotes)"
  cidr_ipv4         = "0.0.0.0/0"
  ip_protocol       = "-1"
}

resource "aws_key_pair" "this" {
  count      = var.existing_key_name == null && local.resolved_ssh_public_key != null ? 1 : 0
  key_name   = "${var.project_name}-${var.environment}-key"
  public_key = local.resolved_ssh_public_key
}
