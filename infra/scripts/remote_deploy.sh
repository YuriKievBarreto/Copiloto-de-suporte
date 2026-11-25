#!/usr/bin/env bash
set -euo pipefail

echo "==> [1/6] Aguardando conclusao do cloud-init (Docker e Git)..."
if command -v cloud-init >/dev/null 2>&1; then
  cloud-init status --wait || true
fi

echo "==> Verificando ferramentas instaladas..."
command -v git >/dev/null 2>&1 || { echo "ERRO: Git nao encontrado"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "ERRO: Docker nao encontrado"; exit 1; }

DOCKER_CMD="docker"
if ! docker info >/dev/null 2>&1; then
  if sudo docker info >/dev/null 2>&1; then
    DOCKER_CMD="sudo docker"
  else
    echo "ERRO: Docker daemon inacessivel"; exit 1
  fi
fi

REPO_DIR="/opt/copiloto-suport"
APP_CONTAINER_NAME="copiloto-api"

echo "==> [2/6] Preparando diretorio do projeto em ${REPO_DIR}..."
sudo mkdir -p "${REPO_DIR}"
sudo chown -R "${USER}:${USER}" "${REPO_DIR}"

cd "${REPO_DIR}"

if [ ! -d ".git" ]; then
  echo "==> Inicializando e clonando repositorio ${GITHUB_REPOSITORY}..."
  git init
  git remote add origin "https://github.com/${GITHUB_REPOSITORY}.git" || git remote set-url origin "https://github.com/${GITHUB_REPOSITORY}.git"
  if [ -n "${GH_TOKEN:-}" ]; then
    AUTH_HEADER="AUTHORIZATION: basic $(printf "x-access-token:%s" "$GH_TOKEN" | base64 | tr -d '\n')"
    git -c "http.extraHeader=${AUTH_HEADER}" fetch --all --tags --prune
  else
    git fetch --all --tags --prune
  fi
else
  echo "==> Atualizando repositorio existente..."
  if [ -n "${GH_TOKEN:-}" ]; then
    AUTH_HEADER="AUTHORIZATION: basic $(printf "x-access-token:%s" "$GH_TOKEN" | base64 | tr -d '\n')"
    git -c "http.extraHeader=${AUTH_HEADER}" fetch --all --tags --prune
  else
    git fetch --all --tags --prune
  fi
fi

echo "==> Fazendo checkout do commit ${COMMIT_SHA}..."
git checkout --force "${COMMIT_SHA}"

if [ -f "${HOME}/copiloto.env" ]; then
  echo "==> Posicionando ${REPO_DIR}/.env..."
  mv -f "${HOME}/copiloto.env" "${REPO_DIR}/.env"
fi

echo "==> [3/6] Validando arquivo .env..."
if [ ! -f "${REPO_DIR}/.env" ]; then
  echo "ERRO: Arquivo ${REPO_DIR}/.env nao encontrado."
  exit 1
fi
chmod 600 "${REPO_DIR}/.env"

echo "==> [4/6] Compilando imagem Docker localmente..."
${DOCKER_CMD} build -f dockerfile -t "${APP_CONTAINER_NAME}:latest" .

echo "==> [5/6] Reiniciando container ${APP_CONTAINER_NAME}..."
if ${DOCKER_CMD} ps -a --format '{{.Names}}' | grep -Eq "^${APP_CONTAINER_NAME}\$"; then
  echo "Removendo container anterior..."
  ${DOCKER_CMD} rm -f "${APP_CONTAINER_NAME}" || true
fi

${DOCKER_CMD} run -d \
  --name "${APP_CONTAINER_NAME}" \
  --restart unless-stopped \
  -p 8000:8000 \
  --env-file "${REPO_DIR}/.env" \
  "${APP_CONTAINER_NAME}:latest"

echo "==> [6/6] Verificando saude local da aplicacao (/health)..."
HEALTH_OK=0
for i in $(seq 1 30); do
  if curl -fsS "http://127.0.0.1:8000/health" >/dev/null 2>&1; then
    HEALTH_OK=1
    echo "Aplicacao respondeu com sucesso apos ${i}s!"
    break
  fi
  sleep 1
done

if [ "$HEALTH_OK" -ne 1 ]; then
  echo "ERRO: Aplicacao nao respondeu em http://127.0.0.1:8000/health dentro de 30s."
  echo "--- Ultimos logs do container ---"
  ${DOCKER_CMD} logs --tail 50 "${APP_CONTAINER_NAME}" || true
  exit 1
fi

echo "==> Limpando imagens orfas do Docker..."
${DOCKER_CMD} image prune -f || true

echo "==> Deploy concluido com sucesso!"
