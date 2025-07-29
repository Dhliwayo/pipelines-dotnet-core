#!/bin/bash

# ArcGIS Server 11.1 Patch Downloader - Linux/macOS Shell Script
# This script downloads all ArcGIS Server 11.1 patches

echo "============================================================"
echo "ArcGIS Server 11.1 Patch Downloader"
echo "============================================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed or not in PATH"
    echo "Please install Python 3.6 or higher and try again"
    exit 1
fi

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.6"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "ERROR: Python version $python_version is too old"
    echo "Please install Python 3.6 or higher and try again"
    exit 1
fi

# Check if patches.json exists
if [ ! -f "Patches/patches.json" ]; then
    echo "ERROR: Patches/patches.json not found"
    echo "Please ensure the patches.json file is in the Patches directory"
    exit 1
fi

# Install dependencies if needed
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Run the patch downloader for Windows patches only
echo
echo "Starting Windows patch download..."
python3 download_arcgis_server_11_1_patches.py --platform windows "$@"

echo
echo "Download completed!"
echo "Check the output directory for downloaded patches" 