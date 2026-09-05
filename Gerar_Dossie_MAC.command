#!/bin/bash
# ==============================================================================
# AGENTE DE INTELIGENCIA COMERCIAL - UFMG HUB / FEIRA DE CARREIRAS (VERSAO MAC)
# ==============================================================================

# Entra automaticamente na pasta onde o script esta localizado
cd "$(dirname "$0")"

clear
echo "=================================================================="
echo " 🤖 AGENTE DE INTELIGENCIA COMERCIAL - UFMG HUB (VERSAO MAC)"
echo "    Geracao Sob Demanda de Dossies Estrategicos (3 Paginas)"
echo "=================================================================="
echo ""

# Verifica se o Python 3 esta instalado
if command -v python3 &> /dev/null; then
    python3 main.py
elif command -v python &> /dev/null; then
    python main.py
else
    echo ""
    echo "❌ [ERRO] Python 3 nao foi encontrado no seu Mac."
    echo "Por favor, instale o Python em: https://www.python.org/downloads/"
    echo ""
    read -p "Pressione ENTER para fechar..."
    exit 1
fi
