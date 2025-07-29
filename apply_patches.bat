@echo off
REM ArcGIS Server 11.1 Windows Patch Applicator - Batch Script
REM This script applies downloaded ArcGIS Server 11.1 Windows patches

echo ============================================================
echo ArcGIS Server 11.1 Windows Patch Applicator
echo ============================================================
echo.

REM Check if running as Administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This script must be run as Administrator
    echo Please right-click Command Prompt and select "Run as Administrator"
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.6 or higher and try again
    pause
    exit /b 1
)

REM Check if patches directory exists
if not exist "arcgis_server_11_1_patches" (
    echo ERROR: Patches directory not found
    echo Please run the download script first:
    echo   python download_arcgis_server_11_1_patches.py
    pause
    exit /b 1
)

REM Check if ArcGIS Server is installed
if not exist "C:\Program Files\ArcGIS\Server" (
    echo WARNING: ArcGIS Server not found at default location
    echo You may need to specify the installation path using --arcgis-install-path
)

REM Install dependencies if needed
echo Installing Python dependencies...
pip install -r requirements_apply.txt

REM Run the patch applicator
echo.
echo Starting patch application...
echo NOTE: This will stop ArcGIS services during the process
echo.
python apply_arcgis_server_11_1_patches.py %*

echo.
echo Patch application completed!
echo Check the logs directory for detailed reports
pause 