@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

where python >nul 2>nul
if %ERRORLEVEL% equ 0 (
    python main.py
    goto end
)

where py >nul 2>nul
if %ERRORLEVEL% equ 0 (
    py main.py
    goto end
)

if exist "C:\Python314\python.exe" (
    "C:\Python314\python.exe" main.py
    goto end
)

echo.
echo [ERRO] Python nao foi encontrado no sistema.
echo Certifique-se de que o Python esta instalado.
echo.
pause

:end
