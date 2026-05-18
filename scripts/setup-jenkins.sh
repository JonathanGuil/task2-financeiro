#!/usr/bin/env bash
# Instala o Jenkins (servidor de Integracao) em container na VM.
# O usuario admin e o job 'task2-pipeline' sao criados automaticamente
# no boot do Jenkins (scripts em ci/init.groovy.d/).
# Uso: sudo bash scripts/setup-jenkins.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

ENV_FILE="ci/.env"

# Gera as credenciais do admin do Jenkins uma unica vez. Ficam em ci/.env,
# que esta no .gitignore — a senha nunca entra no versionamento.
if [ ! -f "$ENV_FILE" ]; then
    echo "==> Gerando credenciais do Jenkins em $ENV_FILE..."
    {
        echo "JENKINS_ADMIN_USER=admin"
        echo "JENKINS_ADMIN_PASSWORD=$(openssl rand -hex 12)"
    } > "$ENV_FILE"
fi

echo "==> Buildando a imagem do Jenkins (Jenkins + Docker CLI + plugins)..."
docker compose --env-file "$ENV_FILE" -f ci/docker-compose.jenkins.yml build

echo "==> Subindo o Jenkins..."
docker compose --env-file "$ENV_FILE" -f ci/docker-compose.jenkins.yml up -d

ADMIN_USER="$(grep '^JENKINS_ADMIN_USER=' "$ENV_FILE" | cut -d= -f2)"
ADMIN_PASS="$(grep '^JENKINS_ADMIN_PASSWORD=' "$ENV_FILE" | cut -d= -f2)"

echo ""
echo "==> Jenkins iniciando em http://<IP-DA-VM>:8080"
echo "    Aguarde cerca de 1 minuto ate ficar pronto."
echo "    Usuario: ${ADMIN_USER}"
echo "    Senha:   ${ADMIN_PASS}"
echo "    (credenciais salvas em ${ENV_FILE}, fora do Git)"
echo "    O job 'task2-pipeline' e criado automaticamente no boot."
