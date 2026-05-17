#!/usr/bin/env bash
# Cria do zero os ambientes de Homologacao e Producao.
# Uso: sudo bash scripts/create-environments.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Buildando a imagem da aplicacao (task2-financeiro:latest)..."
docker build -t task2-financeiro:latest ./app

echo "==> Buildando a imagem do banco (task2-flyway:latest)..."
docker build -t task2-flyway:latest ./db

echo "==> Criando ambiente de HOMOLOGACAO (porta 5003)..."
docker compose -f environments/homolog/docker-compose.yml up -d

echo "==> Criando ambiente de PRODUCAO (porta 5004)..."
docker compose -f environments/prod/docker-compose.yml up -d

echo ""
echo "==> Ambientes criados com sucesso."
echo "    Homologacao -> http://<IP-DA-VM>:5003"
echo "    Producao    -> http://<IP-DA-VM>:5004"
