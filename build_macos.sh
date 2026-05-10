#!/usr/bin/env bash
set -e

echo "Installing dependencies..."
pip3 install -r requirements.txt
pip3 install pyinstaller

echo "Building .app bundle..."
pyinstaller \
  --onefile \
  --windowed \
  --name "CamFilterRecorder" \
  main.py

echo "Done! Find CamFilterRecorder.app in the dist/ folder."
