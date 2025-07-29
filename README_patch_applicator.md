# ArcGIS Server 11.1 Windows Patch Applicator

This script automatically applies downloaded ArcGIS Server 11.1 Windows patches to your ArcGIS Server installation. It handles the entire patch application process including service management, backup creation, and verification.

## Features

- **Automatic Patch Application**: Applies MSP and EXE patches automatically
- **Service Management**: Stops and starts ArcGIS services during patching
- **Backup Creation**: Creates automatic backups before applying patches
- **Critical Patch Filtering**: Option to apply only critical and security patches
- **Detailed Logging**: Comprehensive logging and reporting
- **Verification**: Post-patch verification and service status checking
- **Rollback Ready**: Backup creation enables easy rollback if needed

## Prerequisites

- **Windows Server**: This script is designed for Windows environments
- **Administrator Rights**: Must be run with administrator privileges
- **ArcGIS Server 11.1**: Installed and configured
- **Downloaded Patches**: Patches must be downloaded using the downloader script
- **Python 3.6+**: Required for script execution

## Installation

1. **Install Python dependencies**:
   ```cmd
   pip install -r requirements_apply.txt
   ```

2. **Ensure patches are downloaded**:
   ```cmd
   python download_arcgis_server_11_1_patches.py
   ```

3. **Run as Administrator**: Right-click Command Prompt and select "Run as Administrator"

## Usage

### Basic Usage

Apply all Windows patches to the default ArcGIS Server installation:

```cmd
python apply_arcgis_server_11_1_patches.py
```

### Advanced Usage

**Apply patches from custom directory**:
```cmd
python apply_arcgis_server_11_1_patches.py --patches-dir "D:\my_patches"
```

**Apply only critical and security patches**:
```cmd
python apply_arcgis_server_11_1_patches.py --critical-only
```

**Custom ArcGIS Server installation path**:
```cmd
python apply_arcgis_server_11_1_patches.py --arcgis-install-path "D:\ArcGIS\Server"
```

**Custom backup directory**:
```cmd
python apply_arcgis_server_11_1_patches.py --backup-dir "D:\backups"
```

**Combine multiple options**:
```cmd
python apply_arcgis_server_11_1_patches.py --patches-dir "D:\patches" --critical-only --backup-dir "D:\backups"
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--patches-dir` | Directory containing downloaded patches | `./arcgis_server_11_1_patches` |
| `--arcgis-install-path` | ArcGIS Server installation path | `C:\Program Files\ArcGIS\Server` |
| `--backup-dir` | Directory for backups | `./backups` |
| `--critical-only` | Apply only critical and security patches | `False` |

## Process Overview

The script follows this process:

1. **Pre-flight Checks**
   - Verify ArcGIS Server installation
   - Check service status
   - Validate patch files

2. **Backup Creation**
   - Create timestamped backup of ArcGIS Server
   - Store in specified backup directory

3. **Service Management**
   - Stop ArcGIS services gracefully
   - Wait for services to stop completely

4. **Patch Application**
   - Apply MSP patches using msiexec
   - Apply EXE patches directly
   - Handle critical patches first

5. **Service Restoration**
   - Start ArcGIS services
   - Wait for services to initialize

6. **Verification**
   - Check service status
   - Verify patch application
   - Generate detailed report

## Output and Logging

### Log Files
- **Application Log**: `logs/patch_application_YYYYMMDD_HHMMSS.log`
- **Report**: `logs/patch_application_report_YYYYMMDD_HHMMSS.txt`

### Console Output
- Real-time progress updates
- Service status information
- Success/failure indicators

### Backup Files
- **Backup Directory**: `backups/arcgis_backup_YYYYMMDD_HHMMSS/`
- Complete copy of ArcGIS Server installation

## Patch Types Supported

### MSP Patches
- Applied using `msiexec /p`
- Silent installation mode
- No automatic restart

### EXE Patches
- Applied directly
- Silent installation mode
- No automatic restart

## Critical Patches

Critical patches are identified by:
- `Critical: security`
- `Critical: true`
- `Critical: critical`

These patches are applied first and are essential for security and stability.

## Safety Features

### Automatic Backup
- Creates complete backup before patching
- Enables rollback if needed
- Timestamped for easy identification

### Service Management
- Graceful service stopping
- Proper service restart
- Status verification

### Error Handling
- Detailed error logging
- Continues with remaining patches
- Comprehensive failure reporting

## Troubleshooting

### Common Issues

1. **"Access Denied" errors**
   - Ensure running as Administrator
   - Check file permissions
   - Verify ArcGIS Server installation path

2. **"Service not found" warnings**
   - Normal if some services aren't installed
   - Script continues with available services

3. **"Patch application failed"**
   - Check patch file integrity
   - Verify ArcGIS Server version compatibility
   - Review detailed logs

4. **"Services won't start"**
   - Check system resources
   - Review ArcGIS Server logs
   - Verify configuration files

### Recovery Options

1. **Rollback from Backup**
   ```cmd
   # Stop services
   net stop "ArcGIS Server"
   
   # Restore from backup
   xcopy "backups\arcgis_backup_YYYYMMDD_HHMMSS\*" "C:\Program Files\ArcGIS\Server\" /E /I /Y
   
   # Start services
   net start "ArcGIS Server"
   ```

2. **Manual Patch Application**
   - Apply patches individually using Windows Installer
   - Use ArcGIS Server Manager for verification

## Best Practices

### Before Patching
1. **Test Environment**: Apply patches in test environment first
2. **Backup**: Ensure adequate backup space
3. **Maintenance Window**: Schedule during maintenance window
4. **Documentation**: Document current configuration

### During Patching
1. **Monitor**: Watch console output and logs
2. **Don't Interrupt**: Avoid interrupting the process
3. **Verify**: Check service status after completion

### After Patching
1. **Test**: Verify functionality
2. **Monitor**: Watch for issues
3. **Document**: Update documentation
4. **Cleanup**: Remove old backups if needed

## Security Considerations

- **Administrator Rights**: Required for patch application
- **Backup Security**: Secure backup files appropriately
- **Network Access**: Ensure network connectivity for service restart
- **Audit Trail**: Logs provide audit trail of changes

## Support

For issues related to:
- **Script functionality**: Check troubleshooting section
- **ArcGIS Server issues**: Contact ESRI support
- **Patch compatibility**: Verify patch requirements

## Example Output

```
============================================================
ArcGIS Server 11.1 Windows Patch Applicator
============================================================
2024-01-15 10:30:00 - INFO - Checking ArcGIS Server installation...
2024-01-15 10:30:01 - INFO - ArcGIS Server found at: C:\Program Files\ArcGIS\Server
2024-01-15 10:30:02 - INFO - ✓ ArcGIS Server is running
2024-01-15 10:30:03 - INFO - ArcGIS Server version: 11.1.0.0
2024-01-15 10:30:04 - INFO - Found 15 Windows patches
2024-01-15 10:30:05 - INFO - Creating backup of ArcGIS Server installation...
2024-01-15 10:30:15 - INFO - Backup created at: backups\arcgis_backup_20240115_103005
2024-01-15 10:30:16 - INFO - Stopping ArcGIS services...
2024-01-15 10:30:20 - INFO - ✓ Stopped ArcGIS Server
2024-01-15 10:30:25 - INFO - Applying 15 patches...

[1/15] Processing patch...
============================================================
Applying patch: ArcGIS Server Security 2025 Update 1
QFE ID: S-111-P-1138
Critical: security
Release Date: 04/17/2025
============================================================
2024-01-15 10:30:30 - INFO - Applying MSP patch: ArcGIS-111-S-SEC2025U1-Patch.msp
2024-01-15 10:32:15 - INFO - ✓ Successfully applied ArcGIS-111-S-SEC2025U1-Patch.msp
2024-01-15 10:32:16 - INFO - ✓ Successfully applied all files for ArcGIS Server Security 2025 Update 1

...

2024-01-15 11:15:00 - INFO - Starting ArcGIS services...
2024-01-15 11:15:10 - INFO - ✓ Started ArcGIS Server
2024-01-15 11:15:15 - INFO - Verifying patch application...
2024-01-15 11:15:20 - INFO - ✓ ArcGIS Server is running

============================================================
PATCH APPLICATION SUMMARY
============================================================
Total Patches: 15
Successfully Applied: 15
Failed: 0
============================================================

✓ All patches applied successfully!
```

## License

This script is provided as-is for educational and operational purposes. Please ensure compliance with ESRI's terms of service when applying patches. 