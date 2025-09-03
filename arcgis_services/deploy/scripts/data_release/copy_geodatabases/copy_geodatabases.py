# RSA 2025 

# Copies all the geodatabases from the source to target as specified in the config file, if the update_in_release is set to True

# Imports 

import arcpy 
import configparser
import logging
import logging.handlers
import os 
import sys



class CopyGeodatabases:
    __logger = {}
    
    def __init__(self):

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        script_file = os.path.basename(__file__)
        formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

        # Configure handlers once to avoid duplicated logs if re-instantiated
        if not self.__logger.handlers:
            consoleHandler = logging.StreamHandler(sys.stdout)
            consoleHandler.setLevel(logging.DEBUG)
            consoleHandler.setFormatter(formatter)

            log_dir = os.path.dirname(os.path.realpath(__file__))
            log_path = os.path.join(log_dir, "copy_geodatabases.log")
            fileHandler = logging.handlers.RotatingFileHandler(filename=log_path, maxBytes=1024000, backupCount=10, mode="a")
            fileHandler.setLevel(logging.INFO)
            fileHandler.setFormatter(formatter)

            self.__logger.addHandler(consoleHandler)
            self.__logger.addHandler(fileHandler)

        self.__logger.info("Start")

        config = self.read_config_ini()

        for config_key_arg in config:
            if config_key_arg == 'DEFAULT':
                continue
        
            source_gdb = config[config_key_arg]["source_gdb"]
            target_gdb = config[config_key_arg]["target_gdb"]
            try:
                update_in_release = config[config_key_arg]["update_in_release"]
            except KeyError:
                raise KeyError(f"Missing 'update_in_release' for section '{config_key_arg}' in config.ini")

            should_update_gdb = self.set_should_update_value(update_in_release)

            if should_update_gdb:
                self.__logger.info("{0}...copying {1} to {2}".format(config_key_arg, source_gdb, target_gdb))
                self.execute_copy_gdb(source_gdb, target_gdb)
                self.__logger.info("    ... finished copying {0}".format(target_gdb))
            else:
                 self.__logger.info(config_key_arg + " - Data update for key is set to false and will be ignored") 


        self.__logger.info("End")

    def set_should_update_value(self, update_in_release):
        if isinstance(update_in_release, bool):
            return update_in_release
        value = str(update_in_release).strip().lower()
        if value in ("true", "1", "yes", "on"):            
            return True
        if value in ("false", "0", "no", "off"):
            return False
        raise ValueError("update_in_release parameter is neither True nor False")


    # Functions 

    def read_config_ini(self):
        path = os.path.dirname(os.path.realpath(__file__))
        config_ini_path = os.path.join(path, "config", "config.ini")
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

            # Validate inputs
            if not source_gdb:
                raise ValueError("source_gdb is empty")
            if not target_gdb:
                raise ValueError("target_gdb is empty")

            # Ensure destination directory exists
            target_parent_dir = os.path.dirname(target_gdb)
            if target_parent_dir and not os.path.exists(target_parent_dir):
                os.makedirs(target_parent_dir, exist_ok=True)

            # If target exists, delete first to avoid copy failures
            if arcpy.Exists(target_gdb):
                self.__logger.info("Target exists. Deleting: {0}".format(target_gdb))
                arcpy.management.Delete(target_gdb)

            self.__logger.info("Copying geodatabase using arcpy.Copy_management")
            arcpy.Copy_management(source_gdb, target_gdb)

        except Exception as e:
            self.__logger.exception("Failed to copy geodatabase from '{0}' to '{1}'".format(source_gdb, target_gdb))
            raise

if __name__ == "__main__":
    processor = CopyGeodatabases()

