@echo off
chcp 65001 >nul
setlocal
title Instalar Git y GitHub CLI

echo ============================================================
echo INSTALACION DE REQUISITOS PARA PUBLICAR EN GITHUB
echo ============================================================
echo.

where winget >nul 2>&1
if errorlevel 1 (
    echo No se encontro winget.
    echo Instala Git y GitHub CLI manualmente y vuelve a ejecutar este archivo.
    echo Git: https://git-scm.com/download/win
    echo GitHub CLI: https://cli.github.com/
    pause
    exit /b 1
)

where git >nul 2>&1
if errorlevel 1 (
    echo Instalando Git...
    winget install --id Git.Git -e --source winget
) else (
    echo Git ya esta instalado.
)

where gh >nul 2>&1
if errorlevel 1 (
    echo Instalando GitHub CLI...
    winget install --id GitHub.cli -e --source winget
) else (
    echo GitHub CLI ya esta instalado.
)

echo.
echo Instalacion terminada.
echo Cierra esta ventana y abre una terminal nueva para actualizar el PATH.
echo Despues ejecuta: 02_PUBLICAR_EN_GITHUB.bat
pause
