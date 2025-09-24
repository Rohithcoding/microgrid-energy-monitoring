#!/bin/bash
# Exit on error
set -e

# Install Python 3.10 if not already installed
if ! command -v python3.10 &> /dev/null; then
    echo "Installing Python 3.10..."
    apt-get update
    apt-get install -y python3.10 python3.10-venv python3.10-dev
    update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.10 1
    update-alternatives --set python3 /usr/bin/python3.10
fi

# Create a virtual environment
python3.10 -m venv /opt/render/project/src/.venv
source /opt/render/project/src/.venv/bin/activate

# Upgrade pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt
