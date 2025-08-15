# RSA 2022 

# Import all tiff files into a specified geodabase, overwriting 
# 
# todo
# 
#  -  

import arcpy
import os
import os
import logging
import logging.handlers
from arcpy import env
import sys
import time
from datetime import timedelta
import configparser



rasters_files_to_import =[]
rasters_datasets_to_delete =[]

def populate_input_files(source_directory, rasters_files_to_import, rasters_datasets_to_delete):
    for root, dirs, files in os.walk(source_directory):
        for file in files:
            if file.endswith(".tif"):
                rasters_files_to_import.append(file) 
                rasters_datasets_to_delete.append(file.replace('.tif',''))


def list_datasets_to_overwrite(rasters_datasets_to_delete):
    raster_list = arcpy.ListRasters()
    
    for raster in raster_list:
        if(raster in rasters_datasets_to_delete):
            if arcpy.Exists (raster): 
                arcpy.Delete_management (raster)
                logger.info(f'Raster dataset exists, will be deleted and new one created: {raster}')


def import_raster_data(source_directory, out_geodatabase, rasters_files_to_import):
    newList = []
    for x in rasters_files_to_import:
         z = os.path.join(source_directory, x)
         newList.append(z)
     
    inList = (";".join([i for i in newList]))
    logger.info(inList)
    logger.info('')

    arcpy.RasterToGeodatabase_conversion(inList,out_geodatabase)

def read_config_ini(self):
    path = os.path.dirname(os.path.realpath(__file__))
    config_ini_path = os.path.join(path, "config\config.ini")
    config = configparser.ConfigParser()
    # config.optionxform = str  # Case sensitive config values
    config.read(config_ini_path)
    return config
    
if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    script_file = os.path.basename(__file__)
    formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)

    fileHandler = logging.handlers.RotatingFileHandler(filename="import_rasters.log",maxBytes=1024000, backupCount=10, mode="a")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    logger.info("Start importing filed to geodatabase")

    try:

        config = read_config_ini()

        for config_key_arg in config:
            if config_key_arg == 'DEFAULT':
                continue

            logger.info("Executing for config key " + config_key_arg) 

            source_directory = config[config_key_arg]["source_directory"]
            out_geodatabase = config[config_key_arg]["out_geodatabase"]


            logger.info(f"Importing data from : {source_directory}, to geodb: {out_geodatabase}")
            env.overwriteOutput = True
            logger.info(arcpy.GetMessages())

            tic = time.perf_counter()

            rasters_files_to_import =[]
            rasters_datasets_to_delete =[]

            populate_input_files(source_directory, rasters_files_to_import, rasters_datasets_to_delete)
            list_datasets_to_overwrite(rasters_datasets_to_delete)
            import_raster_data(source_directory, out_geodatabase, rasters_files_to_import)
            toc = time.perf_counter()
            secs = toc - tic
            logger.info(f"Time {timedelta(seconds=secs)}")

    except Exception as e:
        
        logger.error(e)
        raise Exception