#!/bin/bash
set -euo pipefail

# 1. Configurar swapfile de 1 GB (evita OOM em t3.micro durante compilações/builds)
if [ ! -f /swapfile ]; then
  dd if=/dev/zero of=/swapfile bs=128M count=8 status=none
  chmod 600 /swapfile
  mkswap /swapfile
  swapon /swapfile
  echo '/swapfile swap swap defaults 0 0' >> /etc/fstab
fi

# 2. Atualizar pacotes e instalar Docker e Git
dnf update -y
dnf install -y docker git

# 3. Habilitar e iniciar serviço Docker
systemctl enable --now docker
usermod -aG docker ec2-user

# 4. Criar pasta da aplicacao
mkdir -p /opt/copiloto-suport
chown -R ec2-user:ec2-user /opt/copiloto-suport
