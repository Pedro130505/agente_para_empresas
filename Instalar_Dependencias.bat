@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo =====================================================================
echo   INSTALANDO DEPENDENCIAS DO AGENTE COMERCIAL - UFMG HUB
echo =====================================================================
echo.

where pip >nul 2>nul
if %ERRORLEVEL% equ 0 (
    pip install -r requirements.txt
    goto finish
)

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python -m pip install -r requirements.txt
    goto finish
)

if exist "C:\Python314\python.exe" (
    "C:\Python314\python.exe" -m pip install -r requirements.txt
    goto finish
)

echo [ERRO] pip ou Python nao encontrado.
pause
exit /b 1

:finish
echo.
echo =====================================================================
echo   Instalacao concluida com sucesso!
echo   Voce ja pode dar dois cliques no "Gerar_Dossie.bat".
echo =====================================================================
echo.
pause
