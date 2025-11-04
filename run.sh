#!/bin/bash

# Stock Fundamentals Analyzer - Run Script
# This script sets up a virtual environment, installs dependencies, and runs the app

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if ticker argument is provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run.sh <TICKER>"
    echo "Example: ./run.sh AAPL"
    exit 1
fi

TICKER=$1
VENV_DIR="venv"

echo -e "${YELLOW}Setting up environment...${NC}"

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    echo -e "${GREEN}Virtual environment created.${NC}"
else
    echo "Virtual environment already exists."
fi

# Activate virtual environment
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies from requirements.txt..."
    pip install -r requirements.txt --quiet
    echo -e "${GREEN}Dependencies installed.${NC}"
else
    echo "Warning: requirements.txt not found. Installing yfinance..."
    pip install yfinance requests --quiet
fi

# Run the application
echo -e "\n${GREEN}Running stock analysis for ticker: $TICKER${NC}\n"
python stock.py "$TICKER"

# Note: Virtual environment will remain activated after script execution
echo -e "\n${YELLOW}Note: Virtual environment is still active in this shell session.${NC}"

