#!/bin/bash

PLUGIN_DIR="/usr/lib/budgie-desktop/plugins" 

if [ ! -d "$PLUGIN_DIR" ]
then
    echo "The Budgie plugin directory does not exist: $PLUGIN_DIR"
    exit 1
fi

echo "Installing Compact Workspace Switcher to $PLUGIN_DIR"
if sudo cp -r ./src/workspaces-compact-applet "${PLUGIN_DIR}/" && budgie-panel --replace &
then
    echo "Done. You should be able to add the applet to your panel now." 
else
    echo "Install failed"
    exit 1
fi
