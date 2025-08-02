#!/bin/bash

APPDIR="$HOME/.local/share/applications"
DESKTOP_FILE="chihiro.desktop"

# Crée une copie avec le bon chemin
PROJECT_DIR="$(pwd)"
ICON_PATH="$PROJECT_DIR/ui/picture.png"
PYTHON_CMD="$PROJECT_DIR/venv/bin/python"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Version=1.0
Name=Chihiro
Comment=ELF Reverse Engineering Toolkit
Exec=bash -c "cd $PROJECT_DIR && $PYTHON_CMD -m ui.gui"
Icon=$ICON_PATH
Terminal=false
Type=Application
Categories=Development;Utility;
StartupNotify=false
EOF

# Installer
mkdir -p "$APPDIR"
cp "$DESKTOP_FILE" "$APPDIR/"

echo "✅ Fichier installé : $APPDIR/$DESKTOP_FILE"
echo "🧽 Tu peux maintenant chercher 'Chihiro' dans le menu des applications."
