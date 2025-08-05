#!/bin/bash
# TalkScraper Setup Script for Unix/Linux/macOS

echo "================================="
echo "     TalkScraper Setup"
echo "================================="
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    echo "Please install Python 3.8+ and try again"
    exit 1
fi

echo "Python version:"
python3 --version
echo

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "ERROR: Failed to create virtual environment"
        exit 1
    fi
    echo "Virtual environment created successfully"
else
    echo "Virtual environment already exists"
fi
echo

# Activate virtual environment and install dependencies
echo "Activating virtual environment and installing dependencies..."
source venv/bin/activate

echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to install dependencies"
    exit 1
fi

echo
echo "================================="
echo "     Setup Complete!"
echo "================================="
echo
echo "Next steps:"
echo "1. Copy config_template.ini to config.ini"
echo "2. Adjust settings in config.ini if needed"
echo "3. Run: python main.py --phase 1"
echo
echo "To activate virtual environment manually:"
echo "   source venv/bin/activate"
echo
