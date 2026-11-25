output "api_gateway_id" {
  description = "ID do API Gateway (guarde no secret API_GATEWAY_ID do GitHub)."
  value       = aws_apigatewayv2_api.this.id
}

output "api_gateway_integration_id" {
  description = "ID da Integracao backend (guarde no secret API_GATEWAY_INTEGRATION_ID do GitHub)."
  value       = aws_apigatewayv2_integration.backend.id
}

output "api_gateway_url" {
  description = "URL fixa HTTPS do API Gateway para usar no seu frontend do GitHub Pages."
  value       = aws_apigatewayv2_api.this.api_endpoint
}
