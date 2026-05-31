#!/usr/bin/env bash
set -euo pipefail

pip3 install --user --break-system-packages pyinstaller customtkinter 2>/dev/null || true

pyinstaller --onefile --windowed \
    --name "GhostEngineer" \
    --add-data "ui:ui" \
    --hidden-import "customtkinter" \
    --hidden-import "tkinter" \
    --hidden-import "tkinter.filedialog" \
    --hidden-import "ui.dashboard" \
    --hidden-import "ui.settings" \
    --hidden-import "ui.dialogs" \
    main.py

echo ""
echo "Done! Executable at: dist/GhostEngineer"
echo ""
echo "To deploy:"
echo "  cp dist/GhostEngineer ~/Desktop/"
echo "  cp -r data/ ~/.ghost-engineer/   # if you have existing config"
