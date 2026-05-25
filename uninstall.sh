#!/usr/bin/env bash
#=============================================================================
# SpeedMeter — Uninstallation Script for Unix-like Systems
#=============================================================================
set -euo pipefail

INSTALL_DIR="${INSTALL_DIR:-$HOME/.speedmeter}"
SYMLINK_DIR="${SYMLINK_DIR:-$HOME/.local/bin}"

echo "Uninstalling SpeedMeter..."

# Remove symlink
if [ -f "$SYMLINK_DIR/speedmeter" ]; then
    rm -f "$SYMLINK_DIR/speedmeter"
    echo "  Removed symlink: $SYMLINK_DIR/speedmeter"
fi

# Remove installation directory
if [ -d "$INSTALL_DIR" ]; then
    rm -rf "$INSTALL_DIR"
    echo "  Removed installation: $INSTALL_DIR"
fi

# Clean up config/cache
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/speedmeter"
CACHE_DIR="${XDG_CACHE_HOME:-$HOME/.cache}/speedmeter"
LOG_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/speedmeter"

for dir in "$CONFIG_DIR" "$CACHE_DIR" "$LOG_DIR"; do
    if [ -d "$dir" ]; then
        rm -rf "$dir"
        echo "  Removed: $dir"
    fi
done

echo ""
echo "SpeedMeter uninstalled. Data directories cleaned."