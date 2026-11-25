resource "aws_apigatewayv2_api" "this" {
  name          = "${var.project_name}-${var.environment}-http-api"
  protocol_type = "HTTP"
  description   = "HTTP API Gateway persistente para frontend do Copiloto de Suporte (GitHub Pages)"

  cors_configuration {
    allow_origins = var.allowed_origins
    allow_methods = ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"]
    allow_headers = ["Content-Type", "Authorization", "X-Requested-With", "Accept"]
    max_age       = 300
  }
}

# Integração inicial apontando para placeholder (atualizada dinamicamente pelo pipeline com o IP da EC2)
resource "aws_apigatewayv2_integration" "backend" {
  api_id                 = aws_apigatewayv2_api.this.id
  integration_type       = "HTTP_PROXY"
  integration_uri        = "http://127.0.0.1:8000/{proxy}"
  integration_method     = "ANY"
  payload_format_version = "1.0"
}

# Rota catch-all que encaminha qualquer caminho (/health, /chat, /docs, etc.)
resource "aws_apigatewayv2_route" "proxy" {
  api_id    = aws_apigatewayv2_api.this.id
  route_key = "ANY /{proxy+}"
  target    = "integrations/${aws_apigatewayv2_integration.backend.id}"
}

# Stage $default com auto-deploy ativado
resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.this.id
  name        = "$default"
  auto_deploy = true
}
