output "api_gateway_id" {
  description = "ID da REST API (guarde no secret API_GATEWAY_ID do GitHub)."
  value       = aws_api_gateway_rest_api.this.id
}

output "api_gateway_resource_id" {
  description = "ID do recurso proxy (guarde no secret API_GATEWAY_RESOURCE_ID do GitHub)."
  value       = aws_api_gateway_resource.proxy.id
}

output "api_gateway_url" {
  description = "URL fixa HTTPS da REST API para usar no seu frontend do GitHub Pages."
  value       = aws_api_gateway_stage.prod.invoke_url
}
