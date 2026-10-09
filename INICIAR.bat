@echo off
setlocal
chcp 65001 >nul
title UFMG Hub - Gerador de Dossies Comerciais
cd /d "%~dp0"

echo ============================================================
echo   UFMG HUB - GERADOR DE DOSSIES COMERCIAIS
echo   Escola de Engenharia da UFMG - Feira de Carreiras
echo ============================================================
echo.

REM 1. Procura o executavel do Python
set "PY_CMD="

if exist "C:\Python314\python.exe" set "PY_CMD=C:\Python314\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "%LOCALAPPDATA%\Programs\Python\Python314\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python314\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "%LOCALAPPDATA%\Programs\Python\Python313\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python313\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" set "PY_CMD=%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "C:\Python313\python.exe" set "PY_CMD=C:\Python313\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "C:\Python312\python.exe" set "PY_CMD=C:\Python312\python.exe"
if defined PY_CMD goto :FOUND_PY

if exist "C:\Python311\python.exe" set "PY_CMD=C:\Python311\python.exe"
if defined PY_CMD goto :FOUND_PY

python --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=python"
    goto :FOUND_PY
)

py --version >nul 2>&1
if not errorlevel 1 (
    set "PY_CMD=py"
    goto :FOUND_PY
)

:NOT_FOUND
echo [ERRO] Python nao foi encontrado no seu computador!
echo.
echo Para usar este programa, instale o Python:
echo 1. Baixe em: https://www.python.org/downloads/
echo 2. Na instalacao, MARQUE a opcao: "Add Python to PATH"
echo.
pause
exit /b 1

:FOUND_PY
echo Python detectado: %PY_CMD%
echo.

REM 2. Verifica se as bibliotecas estao instaladas
echo [1/2] Verificando dependencias do sistema...
"%PY_CMD%" -c "import streamlit, docx, pandas, openpyxl, requests, dotenv" >nul 2>&1
if not errorlevel 1 goto :DEPS_OK

echo.
echo ============================================================
echo   Instalando bibliotecas necessarias...
echo   Isso leva menos de 1 minuto na primeira inicializacao...
echo ============================================================
echo.

"%PY_CMD%" -m pip install -r requirements.txt
if errorlevel 1 (
    "%PY_CMD%" -m pip install --user -r requirements.txt
)

echo.
echo Dependencias instaladas com sucesso!
echo.

:DEPS_OK
REM 3. Inicia o aplicativo web visual
echo [2/2] Abrindo a plataforma no seu navegador...
echo.
echo ============================================================
echo   SISTEMA PRONTO! O site abrira no seu navegador padrao.
echo   Para encerrar o programa, basta fechar esta janela.
echo ============================================================
echo.

"%PY_CMD%" -m streamlit run app_web.py
pause
