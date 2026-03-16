# Metadata Extraction from ESRI MapX Files

This script extracts metadata from ESRI `.mapx` files into editable formats that can be referenced back to the source files.

## Overview

The `extract_metadata.py` script processes all `.mapx` files in the `metadata_updates` folder and extracts:
- Map-level metadata (title, tags, summary, description, etc.)
- Layer-level metadata for all layers in the map
- Information about whether SourceMetadata is used
- File structure information from the mapx archive

## Requirements

- ArcGIS Pro installed with Python environment
- `arcpy` module (included with ArcGIS Pro)
- Python 3.x

## Usage

1. Place your `.mapx` files in the `metadata_updates` folder (same directory as this script)

2. Run the script:
   ```bash
   python extract_metadata.py
   ```

   Or from ArcGIS Pro Python environment:
   ```python
   exec(open('extract_metadata.py').read())
   ```

## Output

The script creates a `metadata_extracted` subfolder containing:

### For each `.mapx` file:

1. **`{filename}_metadata.json`** - Main editable metadata file in JSON format
   - Contains all extracted metadata
   - Includes source file reference
   - Easy to edit with any text editor
   - Structure includes:
     - `source_reference`: Links back to original mapx file
     - `file_structure`: Information about files in the mapx archive
     - `extracted_metadata`: All metadata properties

2. **`{filename}_metadata.xml`** - XML format metadata (if extraction succeeds)
   - Standard ArcGIS metadata format
   - Can be edited and imported back

3. **`{filename}_reference.txt`** - Human-readable reference file
   - Maps extracted files back to source
   - Shows metadata status and layer counts
   - Quick reference for tracking

### Summary Files:

- **`extraction_summary.json`** - Summary of all processed files
  - Lists all processed files
  - Shows which files use SourceMetadata
  - Reports any errors

- **`metadata_extraction.log`** - Detailed log file
  - Processing details
  - Warnings and errors
  - Debug information

## Metadata Properties Extracted

The script extracts the following metadata properties:

### Map-Level:
- Title
- Tags
- Summary
- Description
- Credits
- Access Constraints
- Use Limitations

### Layer-Level:
- Layer name
- Data source
- Title
- Tags
- Summary
- Description

## SourceMetadata Detection

The script automatically detects whether a mapx file uses SourceMetadata:
- Checks map-level metadata
- Checks all layer metadata
- Reports in the output JSON and reference files

## Editing Metadata

1. Open the `{filename}_metadata.json` file in a text editor
2. Edit the metadata properties as needed
3. The JSON structure is self-documenting with clear property names
4. Save your changes

## Re-importing Metadata

To import edited metadata back into the mapx file, you can:
1. Use ArcGIS Pro's Metadata Importer tool
2. Use `arcpy.conversion.ImportMetadata()` function
3. Or use the XML file if you edited that format

## Troubleshooting

### No metadata extracted
- Check that the mapx file is valid
- Verify ArcGIS Pro can open the file
- Check the log file for specific errors

### SourceMetadata not detected
- The detection is based on XML content analysis
- Some metadata configurations may not be detected
- Check the XML output for manual verification

### Project import errors
- Ensure you have write permissions in temp directories
- Check that ArcGIS Pro is properly installed
- Verify the mapx file is not corrupted

## Notes

- The script processes all `.mapx` files in the folder automatically
- Each run will overwrite previous extractions
- The script creates a backup reference to the source file in each output
- Mapx files are ZIP archives, so the script also extracts structural information

