@echo off
chcp 65001 >nul
title UFMG Hub - Gerador de Dossiês Comerciais
cd /d "%~dp0"

echo ============================================================
echo   🎯 UFMG HUB - GERADOR DE DOSSIÊS COMERCIAIS
echo   Escola de Engenharia da UFMG · Feira de Carreiras
echo ============================================================
echo.

:: 1. Procura o executável do Python
set "PY_CMD="
where python >nul 2>nul && set "PY_CMD=python"
if not defined PY_CMD (
    where py >nul 2>nul && set "PY_CMD=py"
)
if not defined PY_CMD (
    if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
    if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
    if exist "C:\Python314\python.exe" set "PY_CMD=C:\Python314\python.exe"
    if exist "C:\Python312\python.exe" set "PY_CMD=C:\Python312\python.exe"
    if exist "C:\Python311\python.exe" set "PY_CMD=C:\Python311\python.exe"
)

if not defined PY_CMD (
    echo [ERRO] Python não foi encontrado no seu computador!
    echo.
    echo Para usar este programa, instale o Python em 1 minuto:
    echo 1. Baixe em: https://www.python.org/downloads/
    echo 2. Na instalação, MARQUE a caixinha: "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: 2. Verifica se as bibliotecas estão instaladas automaticamente
echo [1/2] Verificando dependências do sistema...
%PY_CMD% -c "import streamlit, docx, pandas, openpyxl, requests, dotenv" >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo.
    echo ============================================================
    echo   Primeira vez abrindo! Instalando bibliotecas necessárias...
    echo   (Isso leva menos de 1 minuto e só acontece na 1ª vez)...
    echo ============================================================
    echo.
    %PY_CMD% -m pip install --quiet -r requirements.txt
    if %ERRORLEVEL% neq 0 (
        %PY_CMD% -m pip install --user -r requirements.txt
    )
    echo.
    echo Dependências instaladas com sucesso!
    echo.
)

:: 3. Inicia o aplicativo web visual
echo [2/2] Abrindo a plataforma no seu navegador...
echo.
echo ============================================================
echo   SISTEMA PRONTO! O site abrirá no seu navegador padrão.
echo   Para encerrar o programa, basta fechar esta janela.
echo ============================================================
echo.

%PY_CMD% -m streamlit run app_web.py
pause
