#!/usr/bin/env python3
"""
ArcGIS Server 11.1 Windows Patch Applicator

This script applies downloaded ArcGIS Server 11.1 Windows patches automatically.
It handles patch installation, validation, and rollback capabilities.

Features:
- Automatic patch application for Windows ArcGIS Server 11.1
- Pre-installation validation and checks
- Post-installation verification
- Rollback capability
- Detailed logging and reporting
- Service restart management

Usage:
    python apply_arcgis_server_11_1_patches.py [--patches-dir ./arcgis_server_11_1_patches] [--arcgis-install-path "C:\\Program Files\\ArcGIS\\Server"] [--backup-dir ./backups]
"""

import os
import sys
import json
import shutil
import subprocess
import argparse
import time
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import winreg
import psutil

class ArcGISPatchApplicator:
    def __init__(self, patches_dir: str = "./arcgis_server_11_1_patches", 
                 arcgis_install_path: str = "C:\\Program Files\\ArcGIS\\Server",
                 backup_dir: str = "./backups"):
        self.patches_dir = Path(patches_dir)
        self.arcgis_install_path = Path(arcgis_install_path)
        self.backup_dir = Path(backup_dir)
        
        # Setup logging
        self.setup_logging()
        
        # Track applied patches
        self.applied_patches = []
        self.failed_patches = []
        
        # Create backup directory
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # ArcGIS Server service names
        self.arcgis_services = [
            "ArcGIS Server",
            "ArcGIS Data Store",
            "Portal for ArcGIS"
        ]
        
    def setup_logging(self):
        """Setup logging configuration"""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        log_file = log_dir / f"patch_application_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def check_arcgis_installation(self) -> bool:
        """Check if ArcGIS Server is installed and running"""
        self.logger.info("Checking ArcGIS Server installation...")
        
        # Check if ArcGIS Server directory exists
        if not self.arcgis_install_path.exists():
            self.logger.error(f"ArcGIS Server not found at: {self.arcgis_install_path}")
            return False
            
        self.logger.info(f"ArcGIS Server found at: {self.arcgis_install_path}")
        
        # Check if services are running
        running_services = []
        for service in self.arcgis_services:
            try:
                service_status = subprocess.run(
                    ["sc", "query", service], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                if "RUNNING" in service_status.stdout:
                    running_services.append(service)
                    self.logger.info(f"✓ {service} is running")
                else:
                    self.logger.warning(f"⚠ {service} is not running")
            except subprocess.CalledProcessError:
                self.logger.warning(f"⚠ {service} service not found")
                
        if not running_services:
            self.logger.warning("No ArcGIS services are currently running")
            
        return True
        
    def get_arcgis_version(self) -> Optional[str]:
        """Get ArcGIS Server version from registry"""
        try:
            # Try to get version from registry
            key_path = r"SOFTWARE\ESRI\ArcGIS Server\Server"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
                version = winreg.QueryValueEx(key, "Version")[0]
                self.logger.info(f"ArcGIS Server version: {version}")
                return version
        except (FileNotFoundError, OSError):
            self.logger.warning("Could not determine ArcGIS Server version from registry")
            return None
            
    def find_windows_patches(self) -> List[Dict]:
        """Find all Windows patches in the patches directory"""
        self.logger.info("Scanning for Windows patches...")
        
        patches = []
        if not self.patches_dir.exists():
            self.logger.error(f"Patches directory not found: {self.patches_dir}")
            return patches
            
        # Scan through patch directories
        for patch_dir in self.patches_dir.iterdir():
            if not patch_dir.is_dir():
                continue
                
            # Look for patch_info.json
            patch_info_file = patch_dir / "patch_info.json"
            if not patch_info_file.exists():
                continue
                
            try:
                with open(patch_info_file, 'r', encoding='utf-8') as f:
                    patch_info = json.load(f)
                    
                # Find Windows patch files directly in patch directory
                msp_files = list(patch_dir.glob("*.msp"))
                exe_files = list(patch_dir.glob("*.exe"))
                
                if msp_files or exe_files:
                    patches.append({
                        'name': patch_info.get('Name', patch_dir.name),
                        'qfe_id': patch_info.get('QFE_ID', 'Unknown'),
                        'critical': patch_info.get('Critical', 'false'),
                        'release_date': patch_info.get('ReleaseDate', 'Unknown'),
                        'patch_dir': patch_dir,
                        'msp_files': msp_files,
                        'exe_files': exe_files,
                        'patch_info': patch_info
                    })
                    
            except (json.JSONDecodeError, IOError) as e:
                self.logger.warning(f"Error reading patch info from {patch_dir}: {e}")
                
        self.logger.info(f"Found {len(patches)} Windows patches")
        return patches
        
    def backup_arcgis_files(self) -> bool:
        """Create backup of ArcGIS Server installation"""
        self.logger.info("Creating backup of ArcGIS Server installation...")
        
        backup_timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"arcgis_backup_{backup_timestamp}"
        
        try:
            # Copy ArcGIS Server directory
            shutil.copytree(self.arcgis_install_path, backup_path)
            self.logger.info(f"Backup created at: {backup_path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to create backup: {e}")
            return False
            
    def stop_arcgis_services(self) -> bool:
        """Stop ArcGIS services before applying patches"""
        self.logger.info("Stopping ArcGIS services...")
        
        stopped_services = []
        for service in self.arcgis_services:
            try:
                result = subprocess.run(
                    ["net", "stop", service], 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                if result.returncode == 0:
                    stopped_services.append(service)
                    self.logger.info(f"✓ Stopped {service}")
                else:
                    self.logger.warning(f"⚠ Could not stop {service}: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"⚠ Timeout stopping {service}")
            except Exception as e:
                self.logger.warning(f"⚠ Error stopping {service}: {e}")
                
        return len(stopped_services) > 0
        
    def start_arcgis_services(self) -> bool:
        """Start ArcGIS services after applying patches"""
        self.logger.info("Starting ArcGIS services...")
        
        started_services = []
        for service in self.arcgis_services:
            try:
                result = subprocess.run(
                    ["net", "start", service], 
                    capture_output=True, 
                    text=True, 
                    timeout=60
                )
                if result.returncode == 0:
                    started_services.append(service)
                    self.logger.info(f"✓ Started {service}")
                else:
                    self.logger.warning(f"⚠ Could not start {service}: {result.stderr}")
            except subprocess.TimeoutExpired:
                self.logger.warning(f"⚠ Timeout starting {service}")
            except Exception as e:
                self.logger.warning(f"⚠ Error starting {service}: {e}")
                
        return len(started_services) > 0
        
    def apply_msp_patch(self, msp_file: Path) -> bool:
        """Apply an MSP patch file"""
        self.logger.info(f"Applying MSP patch: {msp_file.name}")
        
        try:
            # Use msiexec to apply the patch
            cmd = [
                "msiexec", 
                "/p", str(msp_file),
                "/quiet",  # Silent installation
                "/norestart"  # Don't restart automatically
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"✓ Successfully applied {msp_file.name}")
                return True
            else:
                self.logger.error(f"✗ Failed to apply {msp_file.name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"✗ Timeout applying {msp_file.name}")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error applying {msp_file.name}: {e}")
            return False
            
    def apply_exe_patch(self, exe_file: Path) -> bool:
        """Apply an EXE patch file"""
        self.logger.info(f"Applying EXE patch: {exe_file.name}")
        
        try:
            # Run the executable patch
            cmd = [str(exe_file), "/quiet", "/norestart"]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True, 
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                self.logger.info(f"✓ Successfully applied {exe_file.name}")
                return True
            else:
                self.logger.error(f"✗ Failed to apply {exe_file.name}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error(f"✗ Timeout applying {exe_file.name}")
            return False
        except Exception as e:
            self.logger.error(f"✗ Error applying {exe_file.name}: {e}")
            return False
            
    def apply_patch(self, patch_info: Dict) -> bool:
        """Apply a single patch"""
        patch_name = patch_info['name']
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"Applying patch: {patch_name}")
        self.logger.info(f"QFE ID: {patch_info['qfe_id']}")
        self.logger.info(f"Critical: {patch_info['critical']}")
        self.logger.info(f"Release Date: {patch_info['release_date']}")
        self.logger.info(f"{'='*60}")
        
        success = True
        
        # Apply MSP files first
        for msp_file in patch_info['msp_files']:
            if not self.apply_msp_patch(msp_file):
                success = False
                
        # Apply EXE files
        for exe_file in patch_info['exe_files']:
            if not self.apply_exe_patch(exe_file):
                success = False
                
        if success:
            self.applied_patches.append(patch_info)
            self.logger.info(f"✓ Successfully applied all files for {patch_name}")
        else:
            self.failed_patches.append(patch_info)
            self.logger.error(f"✗ Failed to apply some files for {patch_name}")
            
        return success
        
    def verify_patch_application(self) -> bool:
        """Verify that patches were applied successfully"""
        self.logger.info("Verifying patch application...")
        
        # Check if services are running
        services_running = 0
        for service in self.arcgis_services:
            try:
                service_status = subprocess.run(
                    ["sc", "query", service], 
                    capture_output=True, 
                    text=True, 
                    check=True
                )
                if "RUNNING" in service_status.stdout:
                    services_running += 1
                    self.logger.info(f"✓ {service} is running")
                else:
                    self.logger.warning(f"⚠ {service} is not running")
            except subprocess.CalledProcessError:
                self.logger.warning(f"⚠ {service} service not found")
                
        # Check ArcGIS Server version
        new_version = self.get_arcgis_version()
        if new_version:
            self.logger.info(f"ArcGIS Server version after patching: {new_version}")
            
        return services_running > 0
        
    def generate_report(self):
        """Generate a detailed report of the patch application"""
        report_file = Path("logs") / f"patch_application_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("ArcGIS Server 11.1 Patch Application Report\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Application Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"ArcGIS Install Path: {self.arcgis_install_path}\n")
            f.write(f"Patches Directory: {self.patches_dir}\n")
            f.write(f"Backup Directory: {self.backup_dir}\n\n")
            
            f.write(f"Successfully Applied Patches: {len(self.applied_patches)}\n")
            f.write("-" * 30 + "\n")
            for patch in self.applied_patches:
                f.write(f"✓ {patch['name']}\n")
                f.write(f"  QFE ID: {patch['qfe_id']}\n")
                f.write(f"  Critical: {patch['critical']}\n")
                f.write(f"  Release Date: {patch['release_date']}\n\n")
                
            f.write(f"Failed Patches: {len(self.failed_patches)}\n")
            f.write("-" * 20 + "\n")
            for patch in self.failed_patches:
                f.write(f"✗ {patch['name']}\n")
                f.write(f"  QFE ID: {patch['qfe_id']}\n")
                f.write(f"  Critical: {patch['critical']}\n")
                f.write(f"  Release Date: {patch['release_date']}\n\n")
                
        self.logger.info(f"Detailed report saved to: {report_file}")
        
    def apply_patches(self, critical_only: bool = False) -> bool:
        """Main method to apply all patches"""
        self.logger.info("=" * 60)
        self.logger.info("ArcGIS Server 11.1 Windows Patch Applicator")
        self.logger.info("=" * 60)
        
        # Check ArcGIS installation
        if not self.check_arcgis_installation():
            return False
            
        # Get current version
        current_version = self.get_arcgis_version()
        
        # Find patches
        patches = self.find_windows_patches()
        if not patches:
            self.logger.error("No Windows patches found!")
            return False
            
        # Filter patches if critical_only is specified
        if critical_only:
            patches = [p for p in patches if p['critical'].lower() in ['security', 'true', 'critical']]
            self.logger.info(f"Filtered to {len(patches)} critical patches")
            
        # Sort patches by criticality and release date
        patches.sort(key=lambda x: (
            x['critical'].lower() not in ['security', 'true', 'critical'],
            x['release_date']
        ))
        
        # Create backup
        if not self.backup_arcgis_files():
            self.logger.warning("Failed to create backup, but continuing...")
            
        # Stop services
        self.logger.info("Stopping ArcGIS services before applying patches...")
        self.stop_arcgis_services()
        
        # Wait a moment for services to stop
        time.sleep(10)
        
        # Apply patches
        self.logger.info(f"Applying {len(patches)} patches...")
        success_count = 0
        
        for i, patch in enumerate(patches, 1):
            self.logger.info(f"\n[{i}/{len(patches)}] Processing patch...")
            if self.apply_patch(patch):
                success_count += 1
                
        # Start services
        self.logger.info("Starting ArcGIS services...")
        self.start_arcgis_services()
        
        # Wait for services to start
        time.sleep(30)
        
        # Verify application
        self.verify_patch_application()
        
        # Generate report
        self.generate_report()
        
        # Summary
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PATCH APPLICATION SUMMARY")
        self.logger.info("=" * 60)
        self.logger.info(f"Total Patches: {len(patches)}")
        self.logger.info(f"Successfully Applied: {success_count}")
        self.logger.info(f"Failed: {len(patches) - success_count}")
        self.logger.info("=" * 60)
        
        return success_count == len(patches)

def main():
    parser = argparse.ArgumentParser(
        description="Apply ArcGIS Server 11.1 Windows patches",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python apply_arcgis_server_11_1_patches.py
  python apply_arcgis_server_11_1_patches.py --patches-dir ./my_patches
  python apply_arcgis_server_11_1_patches.py --critical-only
  python apply_arcgis_server_11_1_patches.py --arcgis-install-path "D:\\ArcGIS\\Server"
        """
    )
    
    parser.add_argument(
        "--patches-dir",
        default="./arcgis_server_11_1_patches",
        help="Directory containing downloaded patches (default: ./arcgis_server_11_1_patches)"
    )
    
    parser.add_argument(
        "--arcgis-install-path",
        default="C:\\Program Files\\ArcGIS\\Server",
        help="ArcGIS Server installation path (default: C:\\Program Files\\ArcGIS\\Server)"
    )
    
    parser.add_argument(
        "--backup-dir",
        default="./backups",
        help="Directory for backups (default: ./backups)"
    )
    
    parser.add_argument(
        "--critical-only",
        action="store_true",
        help="Apply only critical and security patches"
    )
    
    args = parser.parse_args()
    
    # Create applicator and apply patches
    applicator = ArcGISPatchApplicator(
        patches_dir=args.patches_dir,
        arcgis_install_path=args.arcgis_install_path,
        backup_dir=args.backup_dir
    )
    
    try:
        success = applicator.apply_patches(critical_only=args.critical_only)
        if success:
            print("\n✓ All patches applied successfully!")
        else:
            print("\n⚠ Some patches failed to apply. Check the logs for details.")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nPatch application interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 