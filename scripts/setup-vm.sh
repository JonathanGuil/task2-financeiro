#!/usr/bin/env bash
# =============================================================
#  setup-vm.sh - Provisionamento completo de uma VM zerada.
#
#  Leva a VM de "nada instalado" ate a infraestrutura pronta:
#    1. Ferramentas base (git, curl)
#    2. Docker (conteineres)
#    3. Projeto (clone do repositorio)
#    4. Ambientes de Homologacao e Producao
#    5. Servidor de Integracao (Jenkins)
#
#  Uso numa VM zerada (precisa da senha de sudo):
#    curl -fsSL https://raw.githubusercontent.com/JonathanGuil/task2-financeiro/main/scripts/setup-vm.sh -o setup-vm.sh
#    sudo bash setup-vm.sh
#
#  Se o repositorio ja estiver clonado, rode de dentro dele:
#    sudo bash scripts/setup-vm.sh
#
#  Requisito: VM Linux baseada em Debian/Ubuntu (gerenciador apt).
# =============================================================
set -euo pipefail

REPO_URL="https://github.com/JonathanGuil/task2-financeiro.git"

# --- Precisa ser root: o Docker exige privilegio -------------
if [ "$(id -u)" -ne 0 ]; then
    echo "ERRO: rode com sudo -> sudo bash $0"
    exit 1
fi

# --- Usuario e diretorio de instalacao -----------------------
INSTALL_USER="${SUDO_USER:-root}"
INSTALL_HOME="$(getent passwd "$INSTALL_USER" | cut -d: -f6)"
REPO_DIR="${INSTALL_HOME}/task2"

echo "=============================================="
echo " Provisionamento da VM - task2-financeiro"
echo "=============================================="

# --- 1. Ferramentas base -------------------------------------
echo "==> [1/5] Instalando ferramentas base (git, curl)..."
apt-get update -y
apt-get install -y git curl ca-certificates

# --- 2. Docker (conteineres) ---------------------------------
if command -v docker >/dev/null 2>&1; then
    echo "==> [2/5] Docker ja instalado: $(docker --version)"
else
    echo "==> [2/5] Instalando o Docker..."
    curl -fsSL https://get.docker.com | sh
fi
systemctl enable --now docker

# --- 3. Projeto ----------------------------------------------
# Detecta se este script ja esta dentro de um clone do repo.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "${SCRIPT_DIR}/../environments" ]; then
    ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
    echo "==> [3/5] Projeto ja presente em ${ROOT}"
elif [ -d "${REPO_DIR}/.git" ]; then
    ROOT="$REPO_DIR"
    echo "==> [3/5] Atualizando o projeto em ${ROOT}..."
    git -C "$ROOT" pull --ff-only
    chown -R "${INSTALL_USER}:${INSTALL_USER}" "$ROOT"
else
    echo "==> [3/5] Clonando o projeto em ${REPO_DIR}..."
    git clone "$REPO_URL" "$REPO_DIR"
    chown -R "${INSTALL_USER}:${INSTALL_USER}" "$REPO_DIR"
    ROOT="$REPO_DIR"
fi
cd "$ROOT"

# --- 4. Ambientes de Homologacao e Producao ------------------
echo "==> [4/5] Criando os ambientes de Homologacao e Producao..."
bash scripts/create-environments.sh

# --- 5. Servidor de Integracao (Jenkins) ---------------------
echo "==> [5/5] Subindo o servidor de Integracao (Jenkins)..."
bash scripts/setup-jenkins.sh

# --- Resumo --------------------------------------------------
IP="$(hostname -I | awk '{print $1}')"
echo ""
echo "=============================================="
echo " Infraestrutura provisionada com sucesso!"
echo "=============================================="
echo " Homologacao : http://${IP}:5003"
echo " Producao    : http://${IP}:5004"
echo " Jenkins     : http://${IP}:8080"
echo ""
echo " Aguarde ~1 min e pegue a senha inicial do Jenkins:"
echo "   sudo docker exec jenkins cat /var/jenkins_home/secrets/initialAdminPassword"
echo ""
echo " Depois, no navegador: instalar os plugins sugeridos,"
echo " criar o usuario admin e criar o job 'task2-pipeline'"
echo " (Pipeline script from SCM -> Jenkinsfile)."
echo "=============================================="
