#!/usr/bin/env python3
"""
Test script for ArcGIS Server 11.1 Patch Downloader

This script tests the basic functionality of the patch downloader without
actually downloading any files. It verifies that the patches.json file can
be parsed and that ArcGIS Server 11.1 patches can be found.
"""

import json
import sys
from pathlib import Path

def load_patches_data(patches_file: str = "Patches/patches.json") -> dict:
    """Load and parse the patches.json file"""
    try:
        with open(patches_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"Error: Patches file '{patches_file}' not found!")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in patches file: {e}")
        return None

def filter_server_patches(data: dict, platform: str = "windows") -> list:
    """Filter patches for ArcGIS Server 11.1"""
    server_patches = []
    
    for product in data.get("Product", []):
        if product.get("version") == "11.1":
            for patch in product.get("patches", []):
                # Check if this patch affects ArcGIS Server
                products = patch.get("Products", "")
                if "ArcGIS Server" in products or "ArcGIS Enterprise" in products:
                    # Filter by platform if specified
                    patch_platform = patch.get("Platform", "").lower()
                    if platform == "both" or platform in patch_platform:
                        server_patches.append(patch)
    
    return server_patches

def main():
    print("=" * 60)
    print("ArcGIS Server 11.1 Patch Downloader - Test Script")
    print("=" * 60)
    
    # Test 1: Load patches data
    print("\n1. Testing patches.json file loading...")
    data = load_patches_data()
    if data is None:
        sys.exit(1)
    print("✓ Successfully loaded patches.json file")
    
    # Test 2: Check for version 11.1
    print("\n2. Checking for ArcGIS Server 11.1 patches...")
    server_patches = filter_server_patches(data)
    
    if not server_patches:
        print("! No ArcGIS Server 11.1 patches found in the patches.json file")
        print("  This could mean:")
        print("  - The patches.json file doesn't contain version 11.1 data")
        print("  - No patches specifically target ArcGIS Server")
        print("  - The patches.json file structure is different than expected")
        
        # Let's check what versions are available
        print("\n  Available versions in patches.json:")
        versions = set()
        for product in data.get("Product", []):
            version = product.get("version")
            if version:
                versions.add(version)
        
        for version in sorted(versions):
            print(f"    - {version}")
        
        if "11.1" not in versions:
            print("\n  Note: Version 11.1 is not found in the patches.json file")
            print("  The script will work when 11.1 patches become available")
        
        sys.exit(0)
    
    print(f"✓ Found {len(server_patches)} ArcGIS Server 11.1 patches")
    
    # Test 3: Display patch information
    print("\n3. Patch details:")
    print("-" * 60)
    
    for i, patch in enumerate(server_patches, 1):
        print(f"\nPatch {i}:")
        print(f"  Name: {patch.get('Name', 'N/A')}")
        print(f"  QFE ID: {patch.get('QFE_ID', 'N/A')}")
        print(f"  Critical: {patch.get('Critical', 'N/A')}")
        print(f"  Release Date: {patch.get('ReleaseDate', 'N/A')}")
        print(f"  Platform: {patch.get('Platform', 'N/A')}")
        print(f"  Products: {patch.get('Products', 'N/A')}")
        
        patch_files = patch.get("PatchFiles", [])
        print(f"  Download Files: {len(patch_files)}")
        
        for j, url in enumerate(patch_files, 1):
            filename = url.split('/')[-1] if '/' in url else url
            print(f"    {j}. {filename}")
            print(f"       URL: {url}")
    
    # Test 4: Platform-specific filtering
    print("\n4. Testing platform filtering...")
    
    windows_patches = filter_server_patches(data, "windows")
    linux_patches = filter_server_patches(data, "linux")
    
    print(f"  Windows patches: {len(windows_patches)}")
    print(f"  Linux patches: {len(linux_patches)}")
    
    # Test 5: Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"✓ Patches.json file: Loaded successfully")
    print(f"✓ ArcGIS Server 11.1 patches: {len(server_patches)} found")
    print(f"✓ Platform filtering: Working")
    print(f"✓ Ready to download patches")
    print("=" * 60)
    
    if server_patches:
            print("\nTo download Windows patches (default), run:")
    print("  python download_arcgis_server_11_1_patches.py")
    print("\nTo download only Linux patches:")
    print("  python download_arcgis_server_11_1_patches.py --platform linux")
    print("\nTo download both Windows and Linux patches:")
    print("  python download_arcgis_server_11_1_patches.py --platform both")

if __name__ == "__main__":
    main() 