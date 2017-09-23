#!/bin/bash

PLUGIN_DIR="/usr/lib/budgie-desktop/plugins" 

if [ -d "$PLUGIN_DIR" ]; then
    echo "OK"
else
    echo "The Budgie plugin directory does not exist: $PLUGIN_DIR"
    exit 1
fi

echo "Installing workspaces-compact-applet to $PLUGIN_DIR"
sudo cp -r ./src/workspaces-compact-applet "${PLUGIN_DIR}/"
budgie-panel --replace &
echo "Done. You should be able to add the applet to your panel now."
