# RSA 2022 

# Overwrite a vector dataset with basic schema comparison 

# todo 
# 
# - implement named arguments with argparse 
# - refactor compare fields/metadata into single function? 
# - compare spatial reference 

print("Start replace_data.py")
print("Loading imports...")

# Imports 

import arcpy 
import configparser
import logging
import logging.handlers
import os 
import sys

class ReplaceGeoDbData:
    __validate_bool = True
    __logger = {}
    
    def __init__(self):
        # Logging setup 

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        script_file = os.path.basename(__file__)
        formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)

        fileHandler = logging.handlers.RotatingFileHandler(filename="replace_data.log",maxBytes=1024000, backupCount=10, mode="a")
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)

        self.__logger.addHandler(consoleHandler)
        self.__logger.addHandler(fileHandler)

        self.__logger.info("Start")
        self.__logger.info(arcpy.GetMessages())

        config = self.read_config_ini()

        for config_key_arg in config:
            if config_key_arg == 'DEFAULT':
                continue
        
            self.__logger.info("Executing for config key " + config_key_arg) 

            target_workspace = config[config_key_arg]["target_workspace"]
            target_name = config[config_key_arg]["target"]
            source_workspace = config[config_key_arg]["source_workspace"]
            source_name = config[config_key_arg]["source"]
            validate_flag = config[config_key_arg]["validate"]

            update_in_release = config[config_key_arg]["update_in_release"]

            should_update_gdb_feature_class = self.should_update_gdb_feature_class(update_in_release)

            if should_update_gdb_feature_class:
                if validate_flag.lower() == "true":
                    self.__validate_bool = True
                elif validate_flag.lower() == "false":
                    self.__validate_bool = False
                else: 
                    raise ValueError("Validation parameter is neither True or False")

                target_path = os.path.join(target_workspace, target_name)
                source_dataset_path = os.path.join(source_workspace, source_name)

                # Compare schema for feature class, compare raster properties for raster dataset 

                self.__logger.info("Copying {0} to {1}".format(source_dataset_path, target_path))

                self.execute_replace_data(target_path, source_dataset_path)
            else:
                 self.__logger.info("Data update for key is set to false and will be ignored - " + config_key_arg) 


        self.__logger.info("End")

    # Functions 

    def should_update_gdb_feature_class(self, update_in_release):
        if update_in_release.lower() == "true":
            return True
        elif update_in_release.lower() == "false":
            return False
        else: 
            raise ValueError("update_in_release parameter is neither True or False")

    def _get_field_properties(self,data_path: str) -> list:
        """
        List field name, type, length 

        """
        self.__logger.info("Getting field properties for {}".format(data_path))

        fields = arcpy.ListFields(data_path)

        field_properties  = list((f.name, f.type, f.length) for f in fields)

        field_properties.sort()

        self.__logger.info(str(field_properties))

        return field_properties


    def compare_schema(self,target_path: str, source_path: str) -> bool:
        """ 
        Look for key differences in two feature class or table schema 

        """
        consistent_schema = None
        target_field_properties = self._get_field_properties(target_path)
        source_field_properties = self._get_field_properties(source_path)

        if target_field_properties == source_field_properties:
            consistent_schema = True
        else:
            consistent_schema = False

        return consistent_schema


    def _get_single_raster_property(self,data_path: str, property_name: str):
        """ 
        
        """

        # self.__logger.info("Getting raster properties for {}".format(data_path))

        raster_property = arcpy.GetRasterProperties_management(data_path, property_name).getOutput(0)

        return raster_property


    def _list_raster_properties(self,data_path: str, property_names: list) -> list:
        """ 

        """

        self.__logger.info("Getting raster properties for {}".format(data_path))

        properties = []

        for property_name in property_names:

            property_value = self._get_single_raster_property(data_path, property_name)

            properties.append((property_name, property_value))

        properties.sort()

        self.__logger.info(properties)

        return properties


    def compare_raster_properties(self,target_path: str, source_path: str) -> bool:

        consistent_raster_properties = None

        check_properties = [
            "CELLSIZEX",
            "CELLSIZEY", 
            "VALUETYPE", 
            "BANDCOUNT"
        ]

        target_raster_properties = self._list_raster_properties(target_path, check_properties)

        source_raster_properties = self._list_raster_properties(source_path, check_properties)

        if target_raster_properties == source_raster_properties:

            consistent_raster_properties = True

        else:

            consistent_raster_properties = False

        return consistent_raster_properties


    def _get_metadata_properties(self,data_path: str) -> list:
        """ 
        List title, tags, summary, description, credits, access constraints

        """ 
        self.__logger.info("Getting metadata properties for {}".format(data_path))

        m = arcpy.metadata.Metadata(data_path)

        metadata_properties  = (m.title, m.tags, m.summary, m.description, m.credits, m.accessConstraints) 

        self.__logger.info(str(metadata_properties))

        return metadata_properties


    def compare_metadata(self,target_path: str, source_path: str) -> bool:
        """ 
        Look for key differences in two feature class or table schema 

        """
        consistent_metadata = None

        target_metadata = self._get_metadata_properties(target_path)

        source_metadata = self._get_metadata_properties(source_path)

        if target_metadata == source_metadata:

            consistent_metadata = True

        else:

            consistent_metadata = False

        return consistent_metadata

    def skip_compare(self,target_path: str, source_path: str) -> True: 
        """ 
        Skip detailed validation 
        
        E.g. when changes identified are intended or acceptable 

        """

        self.__logger.info("Skipping detailed comparison for: {0}, {1}".format(target_path, source_path))

        return True

    def read_config_ini(self):
        path = os.path.dirname(os.path.realpath(__file__))
        config_ini_path = os.path.join(path, "config\config.ini")
        config = configparser.ConfigParser()
        # config.optionxform = str  # Case sensitive config values
        config.read(config_ini_path)
        return config

    def execute_replace_data(self,target_path, source_dataset_path):
        """ 
        Execute the replacing of data, will need to be refactored at a later stage

        """
        try: 
            d_source = arcpy.Describe(source_dataset_path)

            if arcpy.Exists(target_path): 
                d_target = arcpy.Describe(target_path)

                source_datatype = d_source.dataType
                target_datatype = d_target.dataType
                source_sref = d_source.spatialReference.name
                target_sref = d_target.spatialReference.name
                
                self.__logger.info("Checking that data types and spatial references are consistent")

                if source_datatype != target_datatype:
                    raise ValueError("Source datatype ({}) does not match target ({})".format(source_datatype, target_datatype))

                elif source_sref != target_sref:
                    raise ValueError("Source spatial reference ({}) does not match target ({})".format(source_sref, target_sref))

            else: 
                self.__logger.info("Target {} does not exist. Creating new dataset")

                self.__validate_bool = False

        except Exception as e:
            self.__logger.error(e)
            raise Exception

        # Add switch to skip schema/raster property validation

        # ToDo use decorators or class to simplify this 

        try: 
            if self.__validate_bool == False:
                compare_test = self.skip_compare
            
            elif source_datatype == target_datatype == "FeatureClass":
                # datatype = "FeatureClass"
                compare_test = self.compare_schema

            elif source_datatype == target_datatype == "RasterDataset":
                # datatype = "RasterDataset"
                compare_test = self.compare_raster_properties
            
            else: 
                raise ValueError("Source and input must both be FeatureClass, or both be RasterDataset")

        except Exception as e:
            self.__logger.error(e)
            raise Exception

        try:
            consistent_schema_or_properties = compare_test(target_path, source_dataset_path)

            if consistent_schema_or_properties != True:
                raise ValueError("Schema or raster properties do not match: {}, {}".format(target_path, source_dataset_path))

        except Exception as e:
            self.__logger.error(e)
            raise Exception

        try: 
            self.__logger.info("Copying updated data from: {}, To: {}".format(source_dataset_path, target_path))
            arcpy.env.overwriteOutput = True

            arcpy.Copy_management(source_dataset_path, target_path)
            arcpy.env.overwriteOutput = False

        except Exception as e:
            self.__logger.error(e)
            raise Exception

        try:
            consistent_metadata = self.compare_metadata(target_path, source_dataset_path)

            if consistent_metadata != True:
                raise ValueError("Metadata do not match after update: {}, {}".format(target_path, source_dataset_path))

        except Exception as e:
            self.__logger.error(e)
            raise Exception
        
        
        self.__logger.info("Update successful: {}".format(target_path))

if __name__ == "__main__":
    processor = ReplaceGeoDbData()

