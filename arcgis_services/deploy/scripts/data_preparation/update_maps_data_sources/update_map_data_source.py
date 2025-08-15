
# Imports 

import arcpy 
import configparser
import logging
import logging.handlers
import os 
import sys

if __name__ == "__main__":
    path = os.path.dirname(os.path.realpath(__file__))
    config_ini_path = os.path.join(path, "config\config.ini")
    config = configparser.ConfigParser()
    # config.optionxform = str  # Case sensitive config values
    config.read(config_ini_path)
    return config


    aprx = arcpy.mp.ArcGISProject(r"C:\Projects\YosemiteNP\Yosemite.aprx")
    lyt = aprx.listLayouts("Main Attractions*")[0]
    lyt.exportToPDF(r"C:\Project\YosemiteNP\Output\Yosemite.pdf", resolution=300)