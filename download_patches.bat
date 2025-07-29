@echo off
REM ArcGIS Server 11.1 Patch Downloader - Windows Batch Script
REM This script downloads all ArcGIS Server 11.1 patches

echo ============================================================
echo ArcGIS Server 11.1 Patch Downloader
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher and try again
    pause
    exit /b 1
)

REM Check if patches.json exists
if not exist "Patches\patches.json" (
    echo ERROR: Patches\patches.json not found
    echo Please ensure the patches.json file is in the Patches directory
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing Python dependencies...
pip install -r requirements.txt

REM Run the patch downloader for Windows patches only
echo.
echo Starting Windows patch download...
python download_arcgis_server_11_1_patches.py --platform windows %*

echo.
echo Download completed!
echo Check the output directory for downloaded patches
pause 