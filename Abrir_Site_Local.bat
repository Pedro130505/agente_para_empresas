@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ============================================================
echo   UFMG HUB - INICIANDO SITE LOCAL DE DOSSIES
echo ============================================================
echo.
echo Abrindo o site no seu navegador em instantes...
echo Pressione Ctrl+C para encerrar quando terminar.
echo.

python -m streamlit run app_web.py
if %ERRORLEVEL% equ 0 (
    goto end
)

where streamlit >nul 2>nul
if %ERRORLEVEL% equ 0 (
    streamlit run app_web.py
    goto end
)

py -m streamlit run app_web.py
if %ERRORLEVEL% equ 0 (
    goto end
)

echo [ERRO] Nao foi possivel iniciar o site local.
pause

:end
