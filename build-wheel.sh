#!/bin/bash

# --- Temporäres Build-Verzeichnis ---
BUILD_DIR=$(mktemp -d)
echo "[INFO] Baue Paket im temporären Verzeichnis: $BUILD_DIR"

# --- Build ---
python3 -m venv "$BUILD_DIR/venv"
source "$BUILD_DIR/venv/bin/activate"
pip install --upgrade pip flit

export FLIT_ALLOW_INVALID=1
flit build

WHEEL_FILE=$(ls -t dist/*.whl | head -n 1)
echo "[INFO] Wheels abgeschlossen $WHEEL_FILE"
deactivate
rm -rf $BUILD_DIR
