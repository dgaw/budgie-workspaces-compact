#!/bin/bash

PLUGIN_DIR="/usr/lib/budgie-desktop/plugins" 

# Pre-install checks
if [ $(id -u) = 0 ]
then
    echo "FAIL: Please run this script as your normal user (not using sudo)."
    exit 1
fi

if [ ! -d "$PLUGIN_DIR" ]
then
    echo "FAIL: The Budgie plugin directory does not exist: $PLUGIN_DIR"
    exit 1
fi

function fail() {
    echo "FAIL: Installation failed. Please note any errors above."
    exit 1
}

# Actual installation
echo "Installing Compact Workspace Switcher to $PLUGIN_DIR"

sudo rm -rf "${PLUGIN_DIR}/workspaces-compact-applet" || fail
sudo cp -r ./src/workspaces-compact-applet "${PLUGIN_DIR}/" || fail
budgie-panel --replace &

echo "Done. You should be able to add the applet to your panel now."
