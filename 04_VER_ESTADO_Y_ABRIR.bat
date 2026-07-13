@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0CONFIGURACION.bat"
title Estado del portafolio en GitHub

where gh >nul 2>&1
if errorlevel 1 (
    echo GitHub CLI no esta instalado.
    pause
    exit /b 1
)

gh auth status >nul 2>&1
if errorlevel 1 (
    echo Inicia sesion primero con: gh auth login
    pause
    exit /b 1
)

for /f "delims=" %%G in ('gh api user --jq .login') do set "GH_USER=%%G"

echo.
echo Ultimas ejecuciones de GitHub Pages:
gh run list --repo "!GH_USER!/%REPO_NAME%" --workflow pages.yml --limit 5
echo.

start "" "https://github.com/!GH_USER!/%REPO_NAME%"
start "" "https://!GH_USER!.github.io/%REPO_NAME%/"
pause
