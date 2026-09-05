#!/bin/bash
# ==============================================================================
# INSTALADOR DE DEPENDENCIAS - UFMG HUB / FEIRA DE CARREIRAS (VERSAO MAC)
# ==============================================================================

# Entra automaticamente na pasta onde o script esta localizado
cd "$(dirname "$0")"

clear
echo "=================================================================="
echo " 📦 INSTALADOR DE DEPENDENCIAS - UFMG HUB (VERSAO MAC)"
echo "=================================================================="
echo ""
echo "Instalando bibliotecas necessarias para o agente..."
echo ""

if command -v pip3 &> /dev/null; then
    pip3 install -r requirements.txt
elif command -v pip &> /dev/null; then
    pip install -r requirements.txt
else
    echo ""
    echo "❌ [ERRO] pip3 nao foi encontrado no seu Mac."
    echo "Certifique-se de que o Python 3 esta instalado."
    echo ""
    read -p "Pressione ENTER para fechar..."
    exit 1
fi

echo ""
echo "=================================================================="
echo " ✅ Instalacao concluida com sucesso no seu Mac!"
echo " Agora voce ja pode abrir o arquivo 'Gerar_Dossie_MAC.command'."
echo "=================================================================="
echo ""
read -p "Pressione ENTER para fechar..."
