#!/usr/bin/env python3
"""
Test script for ArcGIS Server 11.1 Windows Patch Applicator

This script tests the basic functionality of the patch applicator without
actually applying any patches. It verifies that patches can be found and
validates the environment.
"""

import json
import sys
from pathlib import Path
import winreg

def check_arcgis_installation(arcgis_install_path: str = "C:\\Program Files\\ArcGIS\\Server") -> bool:
    """Check if ArcGIS Server is installed"""
    install_path = Path(arcgis_install_path)
    
    print("1. Checking ArcGIS Server installation...")
    if install_path.exists():
        print(f"✓ ArcGIS Server found at: {install_path}")
        return True
    else:
        print(f"✗ ArcGIS Server not found at: {install_path}")
        return False

def get_arcgis_version() -> str:
    """Get ArcGIS Server version from registry"""
    print("2. Checking ArcGIS Server version...")
    
    try:
        key_path = r"SOFTWARE\ESRI\ArcGIS Server\Server"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            version = winreg.QueryValueEx(key, "Version")[0]
            print(f"✓ ArcGIS Server version: {version}")
            return version
    except (FileNotFoundError, OSError) as e:
        print(f"⚠ Could not determine ArcGIS Server version: {e}")
        return "Unknown"

def find_windows_patches(patches_dir: str = "./arcgis_server_11_1_patches") -> list:
    """Find all Windows patches in the patches directory"""
    print("3. Scanning for Windows patches...")
    
    patches = []
    patches_path = Path(patches_dir)
    
    if not patches_path.exists():
        print(f"✗ Patches directory not found: {patches_path}")
        return patches
    
    # Scan through patch directories
    for patch_dir in patches_path.iterdir():
        if not patch_dir.is_dir():
            continue
            
        # Look for patch_info.json
        patch_info_file = patch_dir / "patch_info.json"
        if not patch_info_file.exists():
            continue
            
        try:
            with open(patch_info_file, 'r', encoding='utf-8') as f:
                patch_info = json.load(f)
                
            # Check if this is a Windows patch
            windows_dir = patch_dir / "windows"
            if windows_dir.exists():
                # Find .msp files
                msp_files = list(windows_dir.glob("*.msp"))
                exe_files = list(windows_dir.glob("*.exe"))
                
                if msp_files or exe_files:
                    patches.append({
                        'name': patch_info.get('Name', patch_dir.name),
                        'qfe_id': patch_info.get('QFE_ID', 'Unknown'),
                        'critical': patch_info.get('Critical', 'false'),
                        'release_date': patch_info.get('ReleaseDate', 'Unknown'),
                        'msp_files': len(msp_files),
                        'exe_files': len(exe_files)
                    })
                    
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠ Error reading patch info from {patch_dir}: {e}")
    
    print(f"✓ Found {len(patches)} Windows patches")
    return patches

def check_administrator_rights() -> bool:
    """Check if running with administrator rights"""
    print("4. Checking administrator rights...")
    
    try:
        import ctypes
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        if is_admin:
            print("✓ Running with administrator rights")
            return True
        else:
            print("✗ Not running with administrator rights")
            return False
    except ImportError:
        print("⚠ Could not check administrator rights")
        return False

def check_python_dependencies() -> bool:
    """Check if required Python packages are installed"""
    print("5. Checking Python dependencies...")
    
    required_packages = ['psutil']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package} is installed")
        except ImportError:
            print(f"✗ {package} is not installed")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Install missing packages with: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def main():
    print("=" * 60)
    print("ArcGIS Server 11.1 Windows Patch Applicator - Test Script")
    print("=" * 60)
    
    # Check ArcGIS installation
    arcgis_installed = check_arcgis_installation()
    
    # Get version
    version = get_arcgis_version()
    
    # Check administrator rights
    admin_rights = check_administrator_rights()
    
    # Check dependencies
    dependencies_ok = check_python_dependencies()
    
    # Find patches
    patches = find_windows_patches()
    
    # Display patch details
    if patches:
        print("\n6. Patch details:")
        print("-" * 60)
        
        critical_patches = [p for p in patches if p['critical'].lower() in ['security', 'true', 'critical']]
        regular_patches = [p for p in patches if p['critical'].lower() not in ['security', 'true', 'critical']]
        
        if critical_patches:
            print(f"\nCritical Patches ({len(critical_patches)}):")
            for patch in critical_patches:
                print(f"  • {patch['name']}")
                print(f"    QFE ID: {patch['qfe_id']}")
                print(f"    Critical: {patch['critical']}")
                print(f"    Files: {patch['msp_files']} MSP, {patch['exe_files']} EXE")
        
        if regular_patches:
            print(f"\nRegular Patches ({len(regular_patches)}):")
            for patch in regular_patches[:5]:  # Show first 5
                print(f"  • {patch['name']}")
                print(f"    QFE ID: {patch['qfe_id']}")
                print(f"    Files: {patch['msp_files']} MSP, {patch['exe_files']} EXE")
            
            if len(regular_patches) > 5:
                print(f"  ... and {len(regular_patches) - 5} more patches")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ ArcGIS Server Installation: {'Yes' if arcgis_installed else 'No'}")
    print(f"✓ ArcGIS Server Version: {version}")
    print(f"✓ Administrator Rights: {'Yes' if admin_rights else 'No'}")
    print(f"✓ Python Dependencies: {'Yes' if dependencies_ok else 'No'}")
    print(f"✓ Windows Patches Found: {len(patches)}")
    print("=" * 60)
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    
    if not arcgis_installed:
        print("• Install ArcGIS Server 11.1 or specify correct installation path")
    
    if not admin_rights:
        print("• Run the script as Administrator")
    
    if not dependencies_ok:
        print("• Install missing Python dependencies")
    
    if not patches:
        print("• Download patches first using: python download_arcgis_server_11_1_patches.py")
    
    if arcgis_installed and admin_rights and dependencies_ok and patches:
        print("• Environment is ready for patch application")
        print("\nTo apply all patches:")
        print("  python apply_arcgis_server_11_1_patches.py")
        print("\nTo apply only critical patches:")
        print("  python apply_arcgis_server_11_1_patches.py --critical-only")

if __name__ == "__main__":
    main() 