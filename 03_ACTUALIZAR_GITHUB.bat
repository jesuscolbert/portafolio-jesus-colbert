@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0CONFIGURACION.bat"
title Actualizar portafolio en GitHub

echo ============================================================
echo ACTUALIZAR PORTAFOLIO PUBLICADO
echo ============================================================
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no esta instalado.
    pause
    exit /b 1
)

where gh >nul 2>&1
if errorlevel 1 (
    echo ERROR: GitHub CLI no esta instalado.
    pause
    exit /b 1
)

if not exist ".git" (
    echo Este portafolio todavia no fue publicado desde esta carpeta.
    echo Ejecuta 02_PUBLICAR_EN_GITHUB.bat
    pause
    exit /b 1
)

gh auth status >nul 2>&1
if errorlevel 1 (
    gh auth login --web --git-protocol https
)

for /f "delims=" %%G in ('gh api user --jq .login') do set "GH_USER=%%G"

set "COMMIT_MESSAGE="
set /p "COMMIT_MESSAGE=Descripcion del cambio [Actualizar portafolio]: "
if not defined COMMIT_MESSAGE set "COMMIT_MESSAGE=Actualizar portafolio"

git add .
git diff --cached --quiet
if not errorlevel 1 (
    echo No hay cambios pendientes.
) else (
    git commit -m "!COMMIT_MESSAGE!"
    git push origin main
    if errorlevel 1 (
        echo ERROR: No se pudieron subir los cambios.
        pause
        exit /b 1
    )
    echo Cambios enviados. GitHub Pages se actualizara automaticamente.
)

if defined GH_USER (
    set "SITE_URL=https://!GH_USER!.github.io/%REPO_NAME%/"
    set "ACTIONS_URL=https://github.com/!GH_USER!/%REPO_NAME%/actions"
    start "" "!ACTIONS_URL!"
    timeout /t 3 /nobreak >nul
    start "" "!SITE_URL!"
)

pause
