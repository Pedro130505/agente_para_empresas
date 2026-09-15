#!/bin/bash
# ==============================================================================
# UFMG HUB - INICIAR SITE LOCAL (VERSAO MAC)
# ==============================================================================

cd "$(dirname "$0")"

clear
echo "=================================================================="
echo " 🌐 UFMG HUB - INICIANDO SITE LOCAL DE DOSSIES (MAC)"
echo "=================================================================="
echo ""
echo "Abrindo o site no seu navegador em instantes..."
echo "Pressione Ctrl+C nesta janela quando desejar encerrar."
echo ""

if command -v python3 &> /dev/null; then
    python3 -m streamlit run app_web.py
elif command -v streamlit &> /dev/null; then
    streamlit run app_web.py
else
    echo "❌ Python 3 ou Streamlit nao foram encontrados no seu Mac."
    read -p "Pressione ENTER para fechar..."
fi
