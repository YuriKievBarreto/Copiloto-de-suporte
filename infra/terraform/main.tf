data "aws_ami" "al2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }
}

resource "aws_instance" "api" {
  ami                         = data.aws_ami.al2023.id
  instance_type               = var.instance_type
  subnet_id                   = var.subnet_id
  vpc_security_group_ids      = [aws_security_group.api.id]
  associate_public_ip_address = true
  key_name                    = coalesce(local.effective_existing_key_name, try(aws_key_pair.this[0].key_name, null))
  iam_instance_profile        = aws_iam_instance_profile.ec2.name

  user_data                   = file("${path.module}/user_data.sh")
  user_data_replace_on_change = false

  instance_market_options {
    market_type = "spot"

    spot_options {
      spot_instance_type             = "one-time"
      instance_interruption_behavior = "terminate"
      max_price                      = var.spot_max_price
    }
  }

  root_block_device {
    volume_type           = "gp3"
    volume_size           = var.root_volume_size
    delete_on_termination = true
    encrypted             = true

    tags = {
      Name = "${var.project_name}-${var.environment}-root-volume"
    }
  }

  metadata_options {
    http_endpoint               = "enabled"
    http_tokens                 = "required"
    http_put_response_hop_limit = 2
  }

  lifecycle {
    ignore_changes = [ami]
    precondition {
      condition     = local.effective_existing_key_name != null || local.resolved_ssh_public_key != null
      error_message = "Defina ao menos uma das opções de chave SSH: 'existing_key_name', 'ssh_public_key' ou 'ssh_public_key_path'."
    }
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-spot"
  }
}
