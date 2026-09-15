#!/bin/bash
# ==============================================================================
# SCRIPT DE INSTALACAO AUTOMATICA EM SERVIDOR PROPRIO (UBUNTU / DEBIAN)
# ==============================================================================
set -e

echo "=================================================================="
echo " 🚀 CONFIGURANDO SERVIDOR PARA O UFMG HUB (DOSSIES COMERCIAIS)"
echo "=================================================================="

# Atualiza pacotes do sistema
sudo apt-get update && sudo apt-get upgrade -y

# Instala Docker e Docker Compose se nao existirem
if ! command -v docker &> /dev/null; then
    echo "📦 Instalando Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Sobe a aplicacao usando Docker Compose
echo "🚀 Construindo e iniciando o container..."
sudo docker compose down || true
sudo docker compose up --build -d

echo ""
echo "=================================================================="
echo " ✅ SISTEMA INICIADO COM SUCESSO!"
echo " Acesso direto: http://SEU_IP:8501"
echo "=================================================================="
