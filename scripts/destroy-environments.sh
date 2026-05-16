#!/usr/bin/env bash
# Remove completamente os ambientes de Homologacao e Producao (containers + volumes/dados).
# Uso: sudo bash scripts/destroy-environments.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

echo "==> Removendo ambiente de HOMOLOGACAO..."
docker compose -f environments/homolog/docker-compose.yml down -v || true

echo "==> Removendo ambiente de PRODUCAO..."
docker compose -f environments/prod/docker-compose.yml down -v || true

echo "==> Ambientes removidos."
