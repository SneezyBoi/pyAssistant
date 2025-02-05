#!/bin/bash

# Check if the virtual environment directory exists
if [ -d "./venv" ]; then
    echo "Virtual environment exists."
    # Activate the virtual environment
    source ./venv/bin/activate
    # Upgrade pip
    pip install --upgrade pip
    # Install requirements
    pip install -r requirements.txt
    echo "Requirements installed successfully."
else
    echo "Virtual environment does not exist."
    # Create a new virtual environment
    python3 -m venv ./venv
    # Activate the new virtual environment
    source ./venv/bin/activate
    # Upgrade pip
    pip install --upgrade pip
    # Install requirements
    pip install -r requirements.txt
    echo "Virtual environment created and requirements installed."
fi
