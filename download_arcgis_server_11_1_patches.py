#!/usr/bin/env python3
"""
ArcGIS Server 11.1 Patch Downloader

This script downloads all available patches for ArcGIS Server 11.1 from the patches.json file.
It filters patches that are specifically for ArcGIS Server and downloads them to a local directory.

Features:
- Downloads patches for ArcGIS Server 11.1 only
- Supports both Windows and Linux platforms
- Verifies MD5 checksums when available
- Creates organized directory structure
- Provides download progress and logging
- Handles download errors gracefully

Usage:
    python download_arcgis_server_11_1_patches.py [--platform windows|linux|both] [--output-dir ./patches]
"""

import json
import os
import sys
import hashlib
import argparse
import requests
from urllib.parse import urlparse
from pathlib import Path
import time
from typing import List, Dict, Optional

class ArcGISPatchDownloader:
    def __init__(self, patches_file: str = "Patches/patches.json", output_dir: str = "./arcgis_server_11_1_patches"):
        self.patches_file = patches_file
        self.output_dir = Path(output_dir)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Create output directory structure
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "windows").mkdir(exist_ok=True)
        (self.output_dir / "linux").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        
        self.downloaded_files = []
        self.failed_downloads = []
        
    def load_patches_data(self) -> Dict:
        """Load and parse the patches.json file"""
        try:
            with open(self.patches_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return data
        except FileNotFoundError:
            print(f"Error: Patches file '{self.patches_file}' not found!")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in patches file: {e}")
            sys.exit(1)
    
    def filter_server_patches(self, data: Dict, platform: str = "both") -> List[Dict]:
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
    
    def get_platform_from_url(self, url: str) -> str:
        """Determine platform from download URL"""
        url_lower = url.lower()
        if "linux" in url_lower or ".tar" in url_lower:
            return "linux"
        elif ".msp" in url_lower or ".exe" in url_lower:
            return "windows"
        else:
            return "unknown"
    
    def calculate_md5(self, file_path: Path) -> str:
        """Calculate MD5 hash of a file"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest().upper()
    
    def verify_md5(self, file_path: Path, expected_md5: str) -> bool:
        """Verify MD5 hash of downloaded file"""
        if not expected_md5:
            return True  # Skip verification if no MD5 provided
        
        actual_md5 = self.calculate_md5(file_path)
        return actual_md5 == expected_md5
    
    def download_file(self, url: str, output_path: Path, expected_md5: str = None) -> bool:
        """Download a single file with progress tracking"""
        try:
            print(f"Downloading: {url}")
            print(f"To: {output_path}")
            
            # Check if file already exists
            if output_path.exists():
                print(f"File already exists: {output_path}")
                if expected_md5 and self.verify_md5(output_path, expected_md5):
                    print("✓ MD5 verification passed for existing file")
                    return True
                else:
                    print("! MD5 verification failed for existing file, re-downloading...")
            
            # Download file
            response = self.session.get(url, stream=True, timeout=300)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(output_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Show progress
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"\rProgress: {progress:.1f}% ({downloaded_size}/{total_size} bytes)", end="")
            
            print()  # New line after progress
            
            # Verify MD5 if provided
            if expected_md5:
                if self.verify_md5(output_path, expected_md5):
                    print("✓ MD5 verification passed")
                else:
                    print("✗ MD5 verification failed!")
                    output_path.unlink()  # Delete corrupted file
                    return False
            
            print(f"✓ Successfully downloaded: {output_path.name}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Download failed: {e}")
            return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    def extract_md5_from_patch(self, patch: Dict, filename: str) -> Optional[str]:
        """Extract MD5 hash for a specific file from patch data"""
        md5sums = patch.get("MD5sums", [])
        for md5_entry in md5sums:
            if filename in md5_entry:
                return md5_entry.split(":")[1]
        return None
    
    def download_patches(self, platform: str = "both") -> None:
        """Main method to download all ArcGIS Server 11.1 patches"""
        print("=" * 60)
        print("ArcGIS Server 11.1 Patch Downloader")
        print("=" * 60)
        
        # Load patches data
        print("Loading patches data...")
        data = self.load_patches_data()
        
        # Filter server patches
        print("Filtering ArcGIS Server 11.1 patches...")
        server_patches = self.filter_server_patches(data, platform)
        
        if not server_patches:
            print("No ArcGIS Server 11.1 patches found!")
            return
        
        print(f"Found {len(server_patches)} patches for ArcGIS Server 11.1")
        print()
        
        # Download each patch
        for i, patch in enumerate(server_patches, 1):
            print(f"\n[{i}/{len(server_patches)}] Processing: {patch['Name']}")
            print(f"QFE ID: {patch.get('QFE_ID', 'N/A')}")
            print(f"Critical: {patch.get('Critical', 'N/A')}")
            print(f"Release Date: {patch.get('ReleaseDate', 'N/A')}")
            print(f"Platform: {patch.get('Platform', 'N/A')}")
            
            patch_files = patch.get("PatchFiles", [])
            if not patch_files:
                print("No patch files available for download")
                continue
            
            # Create patch directory
            patch_name = patch['Name'].replace(" ", "_").replace("/", "_").replace(":", "_")
            patch_dir = self.output_dir / patch_name
            patch_dir.mkdir(exist_ok=True)
            
            # Save patch metadata
            metadata_file = patch_dir / "patch_info.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(patch, f, indent=2, ensure_ascii=False)
            
            # Download each patch file
            for url in patch_files:
                filename = os.path.basename(urlparse(url).path)
                if not filename:
                    continue
                
                # Determine platform and set output path
                file_platform = self.get_platform_from_url(url)
                if file_platform == "linux":
                    output_path = patch_dir / "linux" / filename
                    (patch_dir / "linux").mkdir(exist_ok=True)
                elif file_platform == "windows":
                    output_path = patch_dir / "windows" / filename
                    (patch_dir / "windows").mkdir(exist_ok=True)
                else:
                    output_path = patch_dir / filename
                
                # Get expected MD5 if available
                expected_md5 = self.extract_md5_from_patch(patch, filename)
                
                # Download file
                success = self.download_file(url, output_path, expected_md5)
                
                if success:
                    self.downloaded_files.append({
                        'patch_name': patch['Name'],
                        'filename': filename,
                        'url': url,
                        'path': str(output_path),
                        'platform': file_platform
                    })
                else:
                    self.failed_downloads.append({
                        'patch_name': patch['Name'],
                        'filename': filename,
                        'url': url,
                        'error': 'Download failed'
                    })
                
                # Small delay to be respectful to the server
                time.sleep(1)
        
        # Generate summary report
        self.generate_summary_report()
    
    def generate_summary_report(self) -> None:
        """Generate a summary report of the download operation"""
        report_file = self.output_dir / "logs" / "download_summary.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ArcGIS Server 11.1 Patch Download Summary\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Download Date: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Files Downloaded: {len(self.downloaded_files)}\n")
            f.write(f"Failed Downloads: {len(self.failed_downloads)}\n\n")
            
            if self.downloaded_files:
                f.write("Successfully Downloaded Files:\n")
                f.write("-" * 30 + "\n")
                for file_info in self.downloaded_files:
                    f.write(f"Patch: {file_info['patch_name']}\n")
                    f.write(f"File: {file_info['filename']}\n")
                    f.write(f"Platform: {file_info['platform']}\n")
                    f.write(f"Path: {file_info['path']}\n")
                    f.write("-" * 30 + "\n")
            
            if self.failed_downloads:
                f.write("\nFailed Downloads:\n")
                f.write("-" * 20 + "\n")
                for file_info in self.failed_downloads:
                    f.write(f"Patch: {file_info['patch_name']}\n")
                    f.write(f"File: {file_info['filename']}\n")
                    f.write(f"Error: {file_info['error']}\n")
                    f.write("-" * 20 + "\n")
        
        print(f"\n" + "=" * 60)
        print("DOWNLOAD SUMMARY")
        print("=" * 60)
        print(f"Total Files Downloaded: {len(self.downloaded_files)}")
        print(f"Failed Downloads: {len(self.failed_downloads)}")
        print(f"Output Directory: {self.output_dir}")
        print(f"Summary Report: {report_file}")
        print("=" * 60)

def main():
    parser = argparse.ArgumentParser(
        description="Download ArcGIS Server 11.1 patches from patches.json",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python download_arcgis_server_11_1_patches.py
  python download_arcgis_server_11_1_patches.py --platform windows
  python download_arcgis_server_11_1_patches.py --platform linux --output-dir ./my_patches
        """
    )
    
    parser.add_argument(
        "--platform",
        choices=["windows", "linux", "both"],
        default="both",
        help="Platform to download patches for (default: both)"
    )
    
    parser.add_argument(
        "--output-dir",
        default="./arcgis_server_11_1_patches",
        help="Output directory for downloaded patches (default: ./arcgis_server_11_1_patches)"
    )
    
    parser.add_argument(
        "--patches-file",
        default="Patches/patches.json",
        help="Path to patches.json file (default: Patches/patches.json)"
    )
    
    args = parser.parse_args()
    
    # Create downloader and start download
    downloader = ArcGISPatchDownloader(
        patches_file=args.patches_file,
        output_dir=args.output_dir
    )
    
    try:
        downloader.download_patches(platform=args.platform)
    except KeyboardInterrupt:
        print("\n\nDownload interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 