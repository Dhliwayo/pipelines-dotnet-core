# RSA 2025 

# Copies all the geodatabases from the source to target as specified in the config file, if the update_in_release is set to True

print("Start copy_geodatabases.py")
print("Loading imports...")
# Imports 

import arcpy 
import configparser
import logging
import logging.handlers
import os 
import sys
import arcpy


class CopyGeodatabases:
    __logger = {}
    
    def __init__(self):

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        script_file = os.path.basename(__file__)
        formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)

        fileHandler = logging.handlers.RotatingFileHandler(filename="copy_geodatabases.log",maxBytes=1024000, backupCount=10, mode="a")
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
        
            source_gdb = config[config_key_arg]["source_gdb"]
            target_gdb = config[config_key_arg]["target_gdb"]
            update_in_release = config[config_key_arg]["update_in_release"]

            should_update_gdb = self.set_should_upate_value(update_in_release)

            if should_update_gdb:
                self.__logger.info("{0}...copying {1} to {2}".format(config_key_arg,source_gdb, target_gdb))
                self.execute_copy_gdb(source_gdb, target_gdb)
                self.__logger.info("    ... finishined copying {0}".format(target_gdb))
            else:
                 self.__logger.info(config_key_arg + " - Data update for key is set to false and will be ignored") 


        self.__logger.info("End")

    def set_should_upate_value(self, update_in_release):
        if update_in_release.lower() == "true":
            return True
        elif update_in_release.lower() == "false":
            return False
        else: 
            raise ValueError("update_in_release parameter is neither True or False")


    # Functions 

    def read_config_ini(self):
        path = os.path.dirname(os.path.realpath(__file__))
        config_ini_path = os.path.join(path, "config\config.ini")
        config = configparser.ConfigParser()
        # config.optionxform = str  # Case sensitive config values
        config.read(config_ini_path)
        return config

    def execute_copy_gdb(self,source_gdb, target_gdb):
        """ 
        Execute the copying of data

        """
        try:
            arcpy.env.overwriteOutput = True

            arcpy.Copy_management(source_gdb, target_gdb)

        except Exception as e:
            self.__logger.error(e)
            raise Exception

if __name__ == "__main__":
    processor = CopyGeodatabases()

