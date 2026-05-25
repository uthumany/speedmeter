#!/usr/bin/env bash
#=============================================================================
# SpeedMeter — Installation Script for Unix-like Systems (Linux / macOS)
#=============================================================================
# This script installs SpeedMeter and all dependencies.
# Usage:
#   chmod +x install.sh && ./install.sh
#   curl -fsSL https://raw.githubusercontent.com/fameux/speedmeter/main/install.sh | bash
#=============================================================================

set -euo pipefail

# ---- Colors ----
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

PROJECT_NAME="speedmeter"
INSTALL_DIR="${INSTALL_DIR:-$HOME/.speedmeter}"
VENV_DIR="$INSTALL_DIR/venv"
PYTHON="${PYTHON:-python3}"
PIP="$VENV_DIR/bin/pip"

# ---- Banner ----
echo -e "${CYAN}"
echo "  ╔═══════════════════════════════════════════╗"
echo "  ║     SpeedMeter — Internet Speed Meter     ║"
echo "  ║     Interactive Terminal TUI Tool         ║"
echo "  ╚═══════════════════════════════════════════╝"
echo -e "${NC}"

# ---- Check Python ----
echo -e "${BOLD}Checking prerequisites...${NC}"
if ! command -v "$PYTHON" &>/dev/null; then
    echo -e "${RED}Error: Python 3 not found. Please install Python 3.10+.${NC}"
    echo "  macOS: brew install python"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip python3-venv"
    echo "  Fedora: sudo dnf install python3 python3-pip"
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1 | awk '{print $2}')
echo -e "  Python version: ${GREEN}$PY_VERSION${NC}"

# Extract major.minor
PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo -e "${YELLOW}Warning: Python 3.10+ recommended (found $PY_VERSION)${NC}"
fi

# ---- Check git ----
if ! command -v git &>/dev/null; then
    echo -e "${YELLOW}Warning: git not found. Install git for version management.${NC}"
fi

# ---- Create virtual environment ----
echo -e "${BOLD}Creating virtual environment...${NC}"
mkdir -p "$INSTALL_DIR"

if [ ! -d "$VENV_DIR" ]; then
    $PYTHON -m venv "$VENV_DIR"
    echo -e "  ${GREEN}✓${NC} Virtual environment created at $VENV_DIR"
else
    echo -e "  ${YELLOW}•${NC} Virtual environment already exists"
fi

# Activate the venv for package installation
source "$VENV_DIR/bin/activate"

# ---- Upgrade pip ----
echo -e "${BOLD}Upgrading pip...${NC}"
"$PIP" install --upgrade pip setuptools wheel

# ---- Install dependencies ----
echo -e "${BOLD}Installing dependencies...${NC}"
DEPENDENCIES=(
    "speedtest-cli>=2.1.3"
    "rich>=13.7.0"
    "textual>=0.52.0"
    "prompt_toolkit>=3.0.43"
    "psutil>=5.9.8"
    "colorama>=0.4.6"
    "platformdirs>=4.2.0"
    "requests>=2.31.0"
)

for dep in "${DEPENDENCIES[@]}"; do
    echo -ne "  Installing $dep ... "
    if "$PIP" install "$dep" &>/tmp/speedmeter_install.log; then
        echo -e "${GREEN}✓${NC}"
    else
        echo -e "${RED}✗${NC}"
        echo -e "  ${RED}Failed to install $dep. Check /tmp/speedmeter_install.log${NC}"
    fi
done

# ---- Install SpeedMeter package ----
echo -e "${BOLD}Installing SpeedMeter...${NC}"
"$PIP" install -e "$(dirname "$0")" 2>/tmp/speedmeter_pkg_install.log || \
    echo -e "${YELLOW}Note: Run from project dir or install from PyPI${NC}"

# ---- Create launcher script ----
echo -e "${BOLD}Creating launcher...${NC}"
LAUNCHER="$INSTALL_DIR/speedmeter"
cat > "$LAUNCHER" << 'LAUNCHER_EOF'
#!/usr/bin/env bash
# SpeedMeter launcher
VENV_DIR="$(cd "$(dirname "$0")" && pwd)/venv"
if [ ! -d "$VENV_DIR" ]; then
    echo "Error: Virtual environment not found at $VENV_DIR"
    echo "Please run install.sh first."
    exit 1
fi
source "$VENV_DIR/bin/activate"
exec python3 -m speedmeter "$@"
LAUNCHER_EOF
chmod +x "$LAUNCHER"

# ---- Create symlink ----
SYMLINK_DIR="${SYMLINK_DIR:-$HOME/.local/bin}"
mkdir -p "$SYMLINK_DIR"
SYMLINK="$SYMLINK_DIR/speedmeter"
if [ -f "$LAUNCHER" ]; then
    ln -sf "$LAUNCHER" "$SYMLINK"
    echo -e "  ${GREEN}✓${NC} Symlink created: $SYMLINK → $LAUNCHER"
fi

# ---- Print PATH instructions ----
echo ""
echo -e "${BOLD}${GREEN}Installation Complete!${NC}"
echo ""
echo -e "  Run:  ${CYAN}speedmeter${NC}"
echo -e "  Or:   ${CYAN}$LAUNCHER${NC}"
echo ""
echo -e "  Quick test:  ${CYAN}speedmeter --quick${NC}"
echo ""

if [[ ":$PATH:" != *":$SYMLINK_DIR:"* ]]; then
    echo -e "  ${YELLOW}Note:${NC} Add $SYMLINK_DIR to your PATH:"
    echo "    echo 'export PATH=\"\$PATH:$SYMLINK_DIR\"' >> ~/.bashrc"
    echo "    source ~/.bashrc"
fi

echo -e ""
echo -e "  ${CYAN}SpeedMeter v1.0.0 — Happy speed testing! 🚀${NC}"