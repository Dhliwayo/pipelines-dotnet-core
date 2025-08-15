
print("Start register_data.py")
print("Loading imports...")

import arcpy
import logging
import logging.handlers
import os 
import sys
import configparser

class RegisterDataWithGeodatabase:
    __logger = {}

    def __init__(self):

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        script_file = os.path.basename(__file__)
        formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)

        fileHandler = logging.handlers.RotatingFileHandler(filename="register_data.log",maxBytes=1024000, backupCount=10, mode="a")
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

            table_name = config[config_key_arg]["table_name"]
            table_type = config[config_key_arg]["table_type"]
            sql = config[config_key_arg]["sql"]
            objectID = config[config_key_arg]["objectID"]

            workspace = 'C:\\Users\\S01397\\Code\\arcgisserver\\connections\\STAGING_GeoRiskOne_as_GeoRisk_USER.sde'

            # Create a view in the geodatabase
            # if table_type.lower() == "view":
            #     arcpy.management.CreateDatabaseView(workspace,table_name,sql)

            input_table=os.path.join(workspace, table_name)

            # Process: Register With Geodatabase
            self.__logger.info("Registering table {0}".format(input_table))
            arcpy.management.RegisterWithGeodatabase(input_table, objectID)

        self.__logger.info("End")
  
    def read_config_ini(self):
        path = os.path.dirname(os.path.realpath(__file__))
        config_ini_path = os.path.join(path, "config\config.ini")
        config = configparser.ConfigParser()
        # config.optionxform = str  # Case sensitive config values
        config.read(config_ini_path)
        return config
    
if __name__ == "__main__":
    processor = RegisterDataWithGeodatabase()

