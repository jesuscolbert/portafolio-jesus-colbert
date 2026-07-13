# Guía rápida de despliegue

## Método automático recomendado

Ejecuta los archivos en este orden:

1. `01_INSTALAR_REQUISITOS.bat`
2. `02_PUBLICAR_EN_GITHUB.bat`

Para cambios futuros:

3. `03_ACTUALIZAR_GITHUB.bat`

## Qué hace el script de publicación

- Comprueba Git y GitHub CLI.
- Inicia sesión en GitHub.
- Configura el nombre y correo de Git.
- Crea un repositorio público.
- Sube el portafolio.
- Activa GitHub Pages con GitHub Actions.
- Inicia el despliegue.
- Abre la página de Actions y la dirección del sitio.

## Solución manual si GitHub Pages no se activa

Entra al repositorio y abre:

`Settings > Pages > Build and deployment > Source > GitHub Actions`

Después abre la pestaña `Actions` y ejecuta el flujo `Deploy GitHub Pages`.
