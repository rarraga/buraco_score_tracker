#!/bin/bash
# ============================================================
#  build.sh - Genera el ejecutable con PyInstaller
#  Linux / macOS
# ============================================================

echo ""
echo "============================================="
echo "  Buraco - Generador de ejecutable"
echo "============================================="
echo ""

# 1) Verificar Python
if ! command -v python3 &>/dev/null; then
    echo "[ERROR] Python3 no encontrado."
    exit 1
fi

# 2) Instalar PyInstaller
echo "[1/3] Instalando PyInstaller..."
pip3 install pyinstaller --upgrade -q

# 3) Limpiar builds anteriores
echo "[2/3] Limpiando builds anteriores..."
rm -rf build dist Buraco.spec

# 4) Generar ejecutable
echo "[3/3] Generando ejecutable (puede tardar 1-2 minutos)..."
pyinstaller \
    --onefile \
    --windowed \
    --name "Buraco" \
    --add-data "game.py:." \
    --add-data "calculator.py:." \
    --add-data "round_dialog.py:." \
    --add-data "ui.py:." \
    main.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Falló la generación del ejecutable."
    exit 1
fi

echo ""
echo "============================================="
echo "  Listo! El ejecutable está en: dist/Buraco"
echo "============================================="