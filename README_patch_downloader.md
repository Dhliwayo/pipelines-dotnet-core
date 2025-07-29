# ArcGIS Server 11.1 Patch Downloader

This script downloads all available patches for ArcGIS Server 11.1 from the `patches.json` file. It automatically filters patches that are specifically for ArcGIS Server and downloads them to a local directory.

## Features

- **Automatic Filtering**: Only downloads patches for ArcGIS Server 11.1
- **Windows-Only**: Downloads only Windows patches (MSP and EXE files)
- **Linux File Skipping**: Automatically skips Linux files even in mixed patches
- **MD5 Verification**: Verifies downloaded files against provided MD5 checksums
- **Organized Structure**: Creates organized directory structure for downloaded patches
- **Progress Tracking**: Shows download progress and provides detailed logging
- **Error Handling**: Gracefully handles download errors and network issues
- **Resume Capability**: Skips already downloaded files (with MD5 verification)

## Prerequisites

- Python 3.6 or higher
- Internet connection to download patches from ESRI servers
- Access to the `patches.json` file

## Installation

1. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Ensure the patches.json file is available**:
   - The script expects `Patches/patches.json` by default
   - You can specify a different path using the `--patches-file` argument

## Usage

### Basic Usage

Download ArcGIS Server 11.1 patches for Windows (default):

```bash
python download_arcgis_server_11_1_patches.py
```

### Advanced Usage



**Specify custom output directory**:
```bash
python download_arcgis_server_11_1_patches.py --output-dir ./my_patches
```

**Use custom patches.json file**:
```bash
python download_arcgis_server_11_1_patches.py --patches-file /path/to/patches.json
```

**Combine multiple options**:
```bash
python download_arcgis_server_11_1_patches.py --platform windows --output-dir ./windows_patches
```

## Command Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--platform` | Platform to download patches for (`windows`) | `windows` |
| `--output-dir` | Output directory for downloaded patches | `./arcgis_server_11_1_patches` |
| `--patches-file` | Path to patches.json file | `Patches/patches.json` |

## Output Structure

The script creates the following directory structure:

```
arcgis_server_11_1_patches/
├── Patch_Name_1/
│   ├── patch_info.json
│   └── patch_file.msp
├── Patch_Name_2/
│   ├── patch_info.json
│   └── patch_file.exe
└── logs/
    └── download_summary.txt
```

### Directory Contents

- **Patch directories**: Each patch gets its own directory named after the patch
- **patch_info.json**: Contains metadata about the patch (name, QFE ID, criticality, etc.)
- **Windows patch files**: Directly in patch directory (.msp, .exe files)
- **logs/download_summary.txt**: Summary report of the download operation

## Patch Information

Each patch includes the following information:

- **Name**: Descriptive name of the patch
- **QFE_ID**: Unique identifier for the patch
- **Critical**: Criticality level (security, true, false)
- **ReleaseDate**: When the patch was released
- **Platform**: Supported platforms
- **URL**: Link to ESRI support documentation
- **PatchFiles**: Array of download URLs
- **MD5sums**: MD5 checksums for file verification

## Error Handling

The script handles various error scenarios:

- **Network errors**: Retries and reports failed downloads
- **File corruption**: Verifies MD5 checksums and re-downloads if needed
- **Missing files**: Skips patches with no available download files
- **Permission errors**: Reports access issues

## Logging and Reports

The script provides detailed logging:

- **Console output**: Real-time progress and status updates
- **Summary report**: Complete list of downloaded and failed files
- **MD5 verification**: Confirms file integrity

## Security Considerations

- **MD5 Verification**: All downloaded files are verified against provided MD5 checksums
- **HTTPS Downloads**: Uses secure connections when available
- **SSL Certificate Verification**: Disabled to handle ESRI server certificate issues
- **User Agent**: Uses a standard browser user agent for downloads

## Troubleshooting

### Common Issues

1. **"Patches file not found"**
   - Ensure the `patches.json` file exists in the specified location
   - Use `--patches-file` to specify the correct path

2. **"No ArcGIS Server 11.1 patches found"**
   - Verify that the patches.json file contains version 11.1 data
   - Check that patches include "ArcGIS Server" in the Products field

3. **"Download failed"**
   - Check your internet connection
   - Verify that ESRI servers are accessible
   - Some patches may require authentication or have restricted access

4. **"MD5 verification failed"**
   - The downloaded file may be corrupted
   - The script will automatically re-download the file
   - Check your network connection for stability

5. **"SSLError" or "Certificate verification failed"**
   - The script automatically disables SSL certificate verification
   - This is normal for ESRI servers with certificate issues
   - SSL warnings are suppressed to reduce console noise

### Performance Tips

- **Bandwidth**: Downloads can be large; ensure sufficient bandwidth
- **Disk Space**: Ensure adequate disk space for all patches
- **Network Stability**: Use a stable internet connection for large downloads

## Example Output

```
============================================================
ArcGIS Server 11.1 Patch Downloader
============================================================
Loading patches data...
Filtering ArcGIS Server 11.1 patches...
Found 3 patches for ArcGIS Server 11.1

[1/3] Processing: ArcGIS Server 11.1 Security Patch
QFE ID: S-111-P-123
Critical: security
Release Date: 2023-01-15
Platform: Linux,Windows
Downloading: https://gisupdates.esri.com/QFE/S-111-P-123/ArcGIS-111-S-SEC-Patch.msp
To: ./arcgis_server_11_1_patches/ArcGIS_Server_11_1_Security_Patch/windows/ArcGIS-111-S-SEC-Patch.msp
Progress: 100.0% (52428800/52428800 bytes)
✓ MD5 verification passed
✓ Successfully downloaded: ArcGIS-111-S-SEC-Patch.msp

============================================================
DOWNLOAD SUMMARY
============================================================
Total Files Downloaded: 5
Failed Downloads: 0
Output Directory: ./arcgis_server_11_1_patches
Summary Report: ./arcgis_server_11_1_patches/logs/download_summary.txt
============================================================
```

## Support

For issues related to:
- **Script functionality**: Check the troubleshooting section above
- **Patch availability**: Contact ESRI support
- **Download access**: Verify your ESRI account permissions

## License

This script is provided as-is for educational and operational purposes. Please ensure compliance with ESRI's terms of service when downloading patches. 