"""
Extract metadata from ESRI mapx files into editable formats.

This script processes all .mapx files in the metadata_updates folder,
extracts metadata (both SourceMetadata and regular metadata),
and creates editable JSON/XML files that can be referenced back to the source.
"""

import os
import json
import logging
import sys
import arcpy
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import zipfile
import xml.etree.ElementTree as ET


class MetadataExtractor:
    """Extract and manage metadata from ESRI mapx files."""
    
    def __init__(self, input_directory: str, output_directory: str = None):
        """
        Initialize the metadata extractor.
        
        :param input_directory: Directory containing .mapx files
        :param output_directory: Directory to save extracted metadata (defaults to input_directory/metadata_extracted)
        """
        self.input_directory = Path(input_directory)
        self.output_directory = Path(output_directory) if output_directory else self.input_directory / "metadata_extracted"
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Ensure output directory exists
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
            
            # File handler
            log_file = self.input_directory / "metadata_extraction.log"
            file_handler = logging.FileHandler(log_file, mode='a')
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        return logger
    
    def find_mapx_files(self) -> List[Path]:
        """Find all .mapx files in the input directory."""
        mapx_files = list(self.input_directory.glob("*.mapx"))
        self.logger.info(f"Found {len(mapx_files)} .mapx file(s) in {self.input_directory}")
        return mapx_files
    
    def extract_mapx_structure(self, mapx_path: Path) -> Dict:
        """
        Extract structure and metadata from a mapx file.
        Mapx files are ZIP archives containing JSON and other files.
        
        :param mapx_path: Path to the .mapx file
        :return: Dictionary containing file structure and metadata references
        """
        structure = {
            "source_file": str(mapx_path),
            "source_filename": mapx_path.name,
            "files_in_archive": [],
            "has_metadata": False,
            "metadata_files": []
        }
        
        try:
            with zipfile.ZipFile(mapx_path, 'r') as zip_ref:
                file_list = zip_ref.namelist()
                structure["files_in_archive"] = file_list
                
                # Look for metadata-related files
                metadata_files = [f for f in file_list if 'metadata' in f.lower() or f.endswith('.xml')]
                structure["metadata_files"] = metadata_files
                structure["has_metadata"] = len(metadata_files) > 0
                
                # Extract and read main map JSON if present
                map_json_files = [f for f in file_list if f.endswith('.json') and 'map' in f.lower()]
                if map_json_files:
                    for json_file in map_json_files:
                        try:
                            content = zip_ref.read(json_file).decode('utf-8')
                            structure[f"content_{json_file}"] = json.loads(content)
                        except:
                            pass
                            
        except Exception as e:
            self.logger.warning(f"Could not read mapx as ZIP archive: {str(e)}")
            structure["error"] = str(e)
        
        return structure
    
    def extract_metadata_using_arcpy(self, mapx_path: Path) -> Dict:
        """
        Extract metadata from a mapx file using arcpy.
        
        :param mapx_path: Path to the .mapx file
        :return: Dictionary containing extracted metadata
        """
        self.logger.info(f"Extracting metadata from: {mapx_path.name}")
        
        metadata_dict = {
            "source_file": str(mapx_path),
            "source_filename": mapx_path.name,
            "has_source_metadata": False,
            "metadata": {},
            "layers": [],
            "extraction_method": "arcpy"
        }
        
        try:
            # Try to access metadata directly from the mapx file
            # First, try to get metadata using arcpy.metadata
            try:
                map_metadata = arcpy.metadata.Metadata(str(mapx_path))
                
                metadata_dict["metadata"] = {
                    "title": getattr(map_metadata, 'title', None),
                    "tags": getattr(map_metadata, 'tags', None),
                    "summary": getattr(map_metadata, 'summary', None),
                    "description": getattr(map_metadata, 'description', None),
                    "credits": getattr(map_metadata, 'credits', None),
                    "accessConstraints": getattr(map_metadata, 'accessConstraints', None),
                    "useLimitations": getattr(map_metadata, 'useLimitations', None),
                }
                
                # Check for SourceMetadata
                try:
                    xml_string = map_metadata.xml
                    if xml_string and "SourceMetadata" in xml_string:
                        metadata_dict["has_source_metadata"] = True
                except:
                    pass
                    
            except Exception as e:
                self.logger.debug(f"Direct metadata access failed: {str(e)}")
                # Try alternative method using project import
                metadata_dict.update(self._extract_via_project_import(mapx_path))
            
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {mapx_path.name}: {str(e)}")
            metadata_dict["error"] = str(e)
        
        return metadata_dict
    
    def _extract_via_project_import(self, mapx_path: Path) -> Dict:
        """
        Extract metadata by importing mapx into a temporary project.
        
        :param mapx_path: Path to the .mapx file
        :return: Dictionary containing extracted metadata
        """
        result = {
            "extraction_method": "project_import",
            "metadata": {},
            "layers": []
        }
        
        try:
            # Create a temporary project
            import tempfile
            import shutil
            
            temp_dir = tempfile.mkdtemp()
            temp_project = os.path.join(temp_dir, "temp_metadata_extract.aprx")
            
            # Try to create a blank project and import the mapx
            try:
                # Use CURRENT project if available, otherwise create new
                try:
                    aprx = arcpy.mp.ArcGISProject("CURRENT")
                    aprx.saveACopy(temp_project)
                    del aprx
                except:
                    # If CURRENT doesn't work, we'll need to handle this differently
                    self.logger.warning("Could not create temp project from CURRENT")
                    return result
                
                aprx = arcpy.mp.ArcGISProject(temp_project)
                aprx.importDocument(str(mapx_path))
                aprx.save()
                
                # Get maps and extract metadata
                maps = aprx.listMaps('*')
                if maps:
                    map_obj = maps[0]
                    
                    # Extract map-level metadata
                    try:
                        map_meta = arcpy.metadata.Metadata(map_obj)
                        result["metadata"] = {
                            "map_name": map_obj.name,
                            "title": getattr(map_meta, 'title', None),
                            "tags": getattr(map_meta, 'tags', None),
                            "summary": getattr(map_meta, 'summary', None),
                            "description": getattr(map_meta, 'description', None),
                        }
                    except:
                        result["metadata"]["map_name"] = map_obj.name
                    
                    # Extract layer metadata
                    layers = map_obj.listLayers('*')
                    for layer in layers:
                        layer_info = {
                            "layer_name": layer.name,
                            "layer_type": "Unknown"
                        }
                        
                        if hasattr(layer, 'dataSource') and layer.dataSource:
                            layer_info["data_source"] = layer.dataSource
                            try:
                                layer_meta = arcpy.metadata.Metadata(layer.dataSource)
                                layer_info["metadata"] = {
                                    "title": getattr(layer_meta, 'title', None),
                                    "tags": getattr(layer_meta, 'tags', None),
                                    "summary": getattr(layer_meta, 'summary', None),
                                }
                            except:
                                pass
                        
                        result["layers"].append(layer_info)
                
                del aprx
                
            finally:
                # Cleanup
                try:
                    shutil.rmtree(temp_dir)
                except:
                    pass
                    
        except Exception as e:
            self.logger.warning(f"Project import method failed: {str(e)}")
            result["error"] = str(e)
        
        return result
    
    def extract_metadata_as_xml(self, mapx_path: Path) -> Optional[str]:
        """
        Extract metadata as XML using arcpy ExportMetadata.
        
        :param mapx_path: Path to the .mapx file
        :return: XML string or None if extraction fails
        """
        try:
            # Create temporary output path
            temp_xml = self.output_directory / f"{mapx_path.stem}_temp_metadata.xml"
            
            # Export metadata to XML
            arcpy.conversion.ExportMetadata(
                source=str(mapx_path),
                translator='ARCGIS2ARCGIS.xml',  # Export in ArcGIS format
                output=str(temp_xml)
            )
            
            # Read the XML file
            if temp_xml.exists():
                with open(temp_xml, 'r', encoding='utf-8') as f:
                    xml_content = f.read()
                temp_xml.unlink()  # Delete temp file
                return xml_content
                
        except Exception as e:
            self.logger.debug(f"Could not export metadata as XML for {mapx_path.name}: {str(e)}")
        
        return None
    
    def save_metadata(self, metadata_dict: Dict, structure_dict: Dict, mapx_path: Path):
        """
        Save extracted metadata to editable files.
        
        :param metadata_dict: Dictionary containing extracted metadata
        :param structure_dict: Dictionary containing mapx file structure
        :param mapx_path: Path to the source .mapx file
        """
        base_name = mapx_path.stem
        
        # Combine metadata and structure information
        combined_metadata = {
            "source_reference": {
                "source_file": str(mapx_path),
                "source_filename": mapx_path.name,
                "source_path_absolute": str(mapx_path.absolute()),
                "extraction_date": datetime.now().isoformat(),
            },
            "file_structure": structure_dict,
            "extracted_metadata": metadata_dict
        }
        
        # Save as JSON (easier to edit)
        json_path = self.output_directory / f"{base_name}_metadata.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(combined_metadata, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Saved JSON metadata to: {json_path}")
        
        # Also try to save as XML if available
        xml_content = self.extract_metadata_as_xml(mapx_path)
        if xml_content:
            xml_path = self.output_directory / f"{base_name}_metadata.xml"
            with open(xml_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            self.logger.info(f"Saved XML metadata to: {xml_path}")
        
        # Create a reference file that maps output files back to source
        reference_path = self.output_directory / f"{base_name}_reference.txt"
        with open(reference_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("METADATA EXTRACTION REFERENCE\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Source MapX File: {mapx_path.absolute()}\n")
            f.write(f"Source Filename: {mapx_path.name}\n\n")
            f.write("Extracted Files:\n")
            f.write(f"  - JSON Metadata: {json_path.name}\n")
            if xml_content:
                f.write(f"  - XML Metadata: {base_name}_metadata.xml\n")
            f.write(f"  - Reference File: {base_name}_reference.txt\n\n")
            f.write("Metadata Information:\n")
            f.write(f"  - Uses SourceMetadata: {metadata_dict.get('has_source_metadata', False)}\n")
            f.write(f"  - Number of Layers: {len(metadata_dict.get('layers', []))}\n")
            f.write(f"  - Extraction Method: {metadata_dict.get('extraction_method', 'unknown')}\n")
            f.write("\n" + "=" * 80 + "\n")
            f.write("To edit metadata, modify the JSON file and use import tools to update the source.\n")
        
        self.logger.info(f"Saved reference file to: {reference_path}")
    
    def process_all_mapx_files(self):
        """Process all .mapx files in the input directory."""
        mapx_files = self.find_mapx_files()
        
        if not mapx_files:
            self.logger.warning(f"No .mapx files found in {self.input_directory}")
            return
        
        # Create summary file
        summary = {
            "input_directory": str(self.input_directory),
            "output_directory": str(self.output_directory),
            "total_files": len(mapx_files),
            "processed_files": [],
            "errors": []
        }
        
        for mapx_file in mapx_files:
            try:
                self.logger.info(f"Processing: {mapx_file.name}")
                
                # Extract file structure
                structure_dict = self.extract_mapx_structure(mapx_file)
                
                # Extract metadata using arcpy
                metadata_dict = self.extract_metadata_using_arcpy(mapx_file)
                
                # Save all extracted information
                self.save_metadata(metadata_dict, structure_dict, mapx_file)
                
                summary["processed_files"].append({
                    "filename": mapx_file.name,
                    "has_source_metadata": metadata_dict.get("has_source_metadata", False),
                    "layer_count": len(metadata_dict.get("layers", [])),
                    "has_metadata_files": structure_dict.get("has_metadata", False),
                    "status": "success"
                })
                
            except Exception as e:
                error_msg = f"Error processing {mapx_file.name}: {str(e)}"
                self.logger.error(error_msg)
                summary["errors"].append({
                    "filename": mapx_file.name,
                    "error": str(e)
                })
        
        # Save summary
        summary_path = self.output_directory / "extraction_summary.json"
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Processing complete. Summary saved to: {summary_path}")
        self.logger.info(f"Processed {len(summary['processed_files'])} file(s), {len(summary['errors'])} error(s)")


def main():
    """Main entry point for the script."""
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # Input directory is the parent folder (metadata_updates)
    input_directory = script_dir
    
    # Output directory will be a subfolder
    output_directory = script_dir / "metadata_extracted"
    
    extractor = MetadataExtractor(
        input_directory=str(input_directory),
        output_directory=str(output_directory)
    )
    
    extractor.process_all_mapx_files()


if __name__ == "__main__":
    main()

