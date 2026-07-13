@echo off
chcp 65001 >nul
setlocal EnableExtensions EnableDelayedExpansion
cd /d "%~dp0"
call "%~dp0CONFIGURACION.bat"
title Publicar portafolio en GitHub Pages

echo ============================================================
echo PUBLICAR PORTAFOLIO EN GITHUB PAGES
echo ============================================================
echo Repositorio: %REPO_NAME%
echo.

where git >nul 2>&1
if errorlevel 1 (
    echo ERROR: Git no esta instalado.
    echo Ejecuta primero 01_INSTALAR_REQUISITOS.bat
    pause
    exit /b 1
)

where gh >nul 2>&1
if errorlevel 1 (
    echo ERROR: GitHub CLI no esta instalado.
    echo Ejecuta primero 01_INSTALAR_REQUISITOS.bat
    pause
    exit /b 1
)

gh auth status >nul 2>&1
if errorlevel 1 (
    echo Debes iniciar sesion en GitHub.
    echo Se abrira el navegador para autenticarte.
    gh auth login --web --git-protocol https
    if errorlevel 1 (
        echo No se pudo iniciar sesion.
        pause
        exit /b 1
    )
)

gh auth setup-git >nul 2>&1

for /f "delims=" %%G in ('gh api user --jq .login') do set "GH_USER=%%G"
if not defined GH_USER (
    echo ERROR: No se pudo detectar tu usuario de GitHub.
    pause
    exit /b 1
)

echo Usuario detectado: !GH_USER!
echo.

if not exist ".git" (
    echo Inicializando repositorio local...
    git init
)

git branch -M main
git config user.name "%GIT_NAME%"
git config user.email "%GIT_EMAIL%"

echo Preparando archivos...
git add .

git diff --cached --quiet
if errorlevel 1 (
    git commit -m "Publicar portafolio profesional"
) else (
    echo No hay cambios nuevos para confirmar.
)

gh repo view "!GH_USER!/%REPO_NAME%" >nul 2>&1
if errorlevel 1 (
    echo Creando repositorio publico...
    gh repo create "!GH_USER!/%REPO_NAME%" --public --source=. --remote=origin --push --description "%REPO_DESCRIPTION%"
    if errorlevel 1 (
        echo ERROR: No se pudo crear o subir el repositorio.
        pause
        exit /b 1
    )
) else (
    echo El repositorio ya existe. Actualizando...
    git remote get-url origin >nul 2>&1
    if errorlevel 1 (
        git remote add origin "https://github.com/!GH_USER!/%REPO_NAME%.git"
    )
    git push -u origin main
    if errorlevel 1 (
        echo ERROR: No se pudo subir la rama main.
        pause
        exit /b 1
    )
)

echo.
echo Activando GitHub Pages con GitHub Actions...
gh api -X POST "repos/!GH_USER!/%REPO_NAME%/pages" -f build_type=workflow >nul 2>&1
if errorlevel 1 (
    gh api -X PUT "repos/!GH_USER!/%REPO_NAME%/pages" -f build_type=workflow >nul 2>&1
)

echo Iniciando despliegue...
gh workflow run pages.yml --repo "!GH_USER!/%REPO_NAME%" >nul 2>&1

set "SITE_URL=https://!GH_USER!.github.io/%REPO_NAME%/"
set "ACTIONS_URL=https://github.com/!GH_USER!/%REPO_NAME%/actions"

echo.
echo ============================================================
echo PUBLICACION INICIADA
echo ============================================================
echo Sitio: !SITE_URL!
echo Estado: !ACTIONS_URL!
echo.
echo GitHub puede tardar entre 1 y 3 minutos en publicar el sitio.
echo Se abrira la pagina de acciones para que veas el progreso.
echo.

start "" "!ACTIONS_URL!"
timeout /t 4 /nobreak >nul
start "" "!SITE_URL!"

pause
