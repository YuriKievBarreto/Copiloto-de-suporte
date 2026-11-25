output "instance_id" {
  description = "ID da instância EC2 Spot."
  value       = aws_instance.api.id
}

output "public_ip" {
  description = "Endereço IPv4 público da instância."
  value       = aws_instance.api.public_ip
}

output "public_dns" {
  description = "DNS público atribuído pela AWS."
  value       = aws_instance.api.public_dns
}

output "ssh_command" {
  description = "Comando para conexão SSH."
  value       = "ssh ec2-user@${aws_instance.api.public_ip}"
}

output "api_url" {
  description = "URL base da API FastAPI."
  value       = "http://${aws_instance.api.public_ip}:${var.api_port}"
}

output "security_group_id" {
  description = "ID do Security Group provisionado."
  value       = aws_security_group.api.id
}

output "iam_role_arn" {
  description = "ARN da IAM Role associada à EC2 (Bedrock)."
  value       = aws_iam_role.ec2.arn
}
