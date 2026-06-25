#!/bin/bash

# IndoClaw Installation Script
# This script installs IndoClaw to ~/.indoclaw and adds it to the system PATH

set -e

echo ""
echo ""
echo ""
echo "███████████████████████████████████████████████████████████████████████████████████████████████████████████████████";
echo "█▌                                                                                                               ▐█";
echo "█▌                                                                                                               ▐█";
echo "█▌   █████ ██████   █████ ██████████      ███████      █████████  █████         █████████   █████   ███   █████  ▐█";
echo "█▌  ░░███ ░░██████ ░░███ ░░███░░░░███   ███░░░░░███   ███░░░░░███░░███         ███░░░░░███ ░░███   ░███  ░░███   ▐█";
echo "█▌   ░███  ░███░███ ░███  ░███   ░░███ ███     ░░███ ███     ░░░  ░███        ░███    ░███  ░███   ░███   ░███   ▐█";
echo "█▌   ░███  ░███░░███░███  ░███    ░███░███      ░███░███          ░███        ░███████████  ░███   ░███   ░███   ▐█";
echo "█▌   ░███  ░███ ░░██████  ░███    ░███░███      ░███░███          ░███        ░███░░░░░███  ░░███  █████  ███    ▐█";
echo "█▌   ░███  ░███  ░░█████  ░███    ███ ░░███     ███ ░░███     ███ ░███      █ ░███    ░███   ░░░█████░█████░     ▐█";
echo "█▌   █████ █████  ░░█████ ██████████   ░░░███████░   ░░█████████  ███████████ █████   █████    ░░███ ░░███       ▐█";
echo "█▌  ░░░░░ ░░░░░    ░░░░░ ░░░░░░░░░░      ░░░░░░░      ░░░░░░░░░  ░░░░░░░░░░░ ░░░░░   ░░░░░      ░░░   ░░░        ▐█";
echo "█▌                                                                                                               ▐█";
echo "█▌                                                                                                               ▐█";
echo "███████████████████████████████████████████████████████████████████████████████████████████████████████████████████";
echo ""
echo ""
echo ""
echo ""
echo "=============================================="
echo "    IndoClaw - Autonomous AI Agent OS"
echo "    Installing..."
echo "=============================================="
echo ""

# Detect OS
OS="$(uname -s)"
echo "Detected OS: $OS"
echo ""

# Function to print error and exit
error_exit() {
    echo "ERROR: $1"
    exit 1
}

# Check if Python 3.10+ is installed
echo "Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | sed 's/Python //')
    echo "Python found: $PYTHON_VERSION"

    # Extract major and minor version
    MAJOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f1)
    MINOR=$(echo "$PYTHON_VERSION" | cut -d'.' -f2)

    if [ "$MAJOR" -lt 3 ] || ([ "$MAJOR" -eq 3 ] && [ "$MINOR" -lt 10 ]); then
        error_exit "Python 3.10+ is required. You have Python $PYTHON_VERSION"
    fi
else
    error_exit "Python 3.10+ is not installed."
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
    error_exit "pip is not installed."
fi

# Installation directory (hidden folder in home)
INDOCLAW_DIR="$HOME/.indoclaw"
echo "Installation directory: $INDOCLAW_DIR"
echo ""

# Check if venv already exists
VENV_EXISTS=false
if [ -d "$INDOCLAW_DIR/venv" ]; then
    echo "Virtual environment already exists at $INDOCLAW_DIR/venv"
    echo ""
    read -p "Reinstall? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
    VENV_EXISTS=true
    rm -rf "$INDOCLAW_DIR/venv"
fi

# Create installation directory
mkdir -p "$INDOCLAW_DIR"

# Copy source to installation directory
echo "Copying source files to $INDOCLAW_DIR..."
cp -r "$(dirname "${BASH_SOURCE[0]}")"/* "$INDOCLAW_DIR/"

# Create a virtual environment
echo "Creating virtual environment..."
python3 -m venv "$INDOCLAW_DIR/venv"
echo "Virtual environment created."
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source "$INDOCLAW_DIR/venv/bin/activate"

# Install pip if not present (Python 3.14+ may not have it by default)
echo "Checking pip installation..."
if ! command -v pip &> /dev/null; then
    echo "Installing pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py | python
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip

# Install IndoClaw package
echo "Installing IndoClaw and dependencies..."
python -m pip install -e "$INDOCLAW_DIR"

# Deactivate virtual environment
deactivate

echo ""
echo "=============================================="
echo "    Installation Complete!"
echo "=============================================="
echo ""
echo "To use IndoClaw, add the virtual environment's bin directory to your PATH."
echo ""
echo "Add this line to your shell configuration file (~/.bashrc, ~/.zshrc, or ~/.profile):"
echo ""
echo "    export PATH=\"\$PATH:$INDOCLAW_DIR/venv/bin\""
echo ""
echo "Then reload your shell configuration:"
echo ""
echo "    source ~/.bashrc   # or ~/.zshrc / ~/.profile"
echo ""
echo "Or run this command to add it automatically:"
echo ""

SHELL_FILE=""
if [ -f "$HOME/.zshrc" ]; then
    SHELL_FILE="$HOME/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    SHELL_FILE="$HOME/.bashrc"
else
    SHELL_FILE="$HOME/.profile"
fi

if [ -f "$HOME/.zshrc" ]; then
    echo "    echo 'export PATH=\"\$PATH:$INDOCLAW_DIR/venv/bin\"' >> ~/.zshrc"
    echo "    source ~/.zshrc"
elif [ -f "$HOME/.bashrc" ]; then
    echo "    echo 'export PATH=\"\$PATH:$INDOCLAW_DIR/venv/bin\"' >> ~/.bashrc"
    echo "    source ~/.bashrc"
else
    echo "    echo 'export PATH=\"\$PATH:$INDOCLAW_DIR/venv/bin\"' >> ~/.profile"
    echo "    source ~/.profile"
fi
echo ""
echo "After updating PATH, verify installation:"
echo "   indoclaw --help"
echo ""
echo "=============================================="

# Ask if user wants to add to PATH automatically
echo ""
read -p "Add IndoClaw to PATH automatically? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Check if already added
    if grep -q "indoclaw.*venv/bin" "$SHELL_FILE" 2>/dev/null; then
        echo "IndoClaw already found in $SHELL_FILE"
    else
        echo "export PATH=\"\$PATH:$INDOCLAW_DIR/venv/bin\" # IndoClaw" >> "$SHELL_FILE"
        echo "Added to $SHELL_FILE"
        echo ""
        echo "Reloading shell configuration..."
        source "$SHELL_FILE"
    fi

    # Verify installation
    if command -v indoclaw &> /dev/null; then
        echo ""
        echo "IndoClaw is now available in your PATH!"
        echo "Run 'indoclaw --help' to get started."
    else
        echo ""
        echo "Installation complete. Please reload your shell or open a new terminal."
    fi
fi
