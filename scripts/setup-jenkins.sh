#!/usr/bin/env bash
# Instala o Jenkins (servidor de Integracao) em container na VM.
# Uso: sudo bash scripts/setup-jenkins.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Buildando a imagem do Jenkins (Jenkins + Docker CLI)..."
docker compose -f ci/docker-compose.jenkins.yml build

echo "==> Subindo o Jenkins..."
docker compose -f ci/docker-compose.jenkins.yml up -d

echo ""
echo "==> Jenkins iniciando em http://<IP-DA-VM>:8080"
echo "    Aguarde cerca de 1 minuto e pegue a senha inicial com:"
echo "    sudo docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
