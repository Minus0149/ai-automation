#!/bin/bash

echo "Starting Automation Project..."
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is not installed or not in PATH"
    exit 1
fi

# Install dependencies
echo "Installing dependencies..."
python3 -m pip install -r requirements.txt

# Create directories
mkdir -p logs screenshots results

# Run automation
echo
echo "Starting automation..."
python3 src/main_automation.py

echo
echo "Automation completed. Check the results directory for output."
