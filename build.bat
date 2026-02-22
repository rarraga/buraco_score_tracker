@echo off
:: ============================================================
::  build.bat - Genera Buraco.exe con PyInstaller
::  Ejecutar desde la carpeta raíz del proyecto
:: ============================================================

echo.
echo =============================================
echo   Buraco - Generador de ejecutable (.exe)
echo =============================================
echo.

:: 1) Verificar que Python esté instalado
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Descargalo de https://www.python.org
    pause
    exit /b 1
)

:: 2) Instalar / actualizar PyInstaller
echo [1/3] Instalando PyInstaller...
pip install pyinstaller --upgrade -q
if errorlevel 1 (
    echo [ERROR] No se pudo instalar PyInstaller.
    pause
    exit /b 1
)

:: 3) Limpiar builds anteriores
echo [2/3] Limpiando builds anteriores...
if exist build   rmdir /s /q build
if exist dist    rmdir /s /q dist
if exist Buraco.spec del /q Buraco.spec

:: 4) Generar el .exe
echo [3/3] Generando Buraco.exe (puede tardar 1-2 minutos)...
pyinstaller ^
    --onefile ^
    --windowed ^
    --name "Buraco" ^
    --add-data "game.py;." ^
    --add-data "calculator.py;." ^
    --add-data "round_dialog.py;." ^
    --add-data "ui.py;." ^
    main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Fallo la generacion del ejecutable.
    pause
    exit /b 1
)

echo.
echo =============================================
echo   Listo! El ejecutable esta en:
echo   dist\Buraco.exe
echo =============================================
echo.
pause