

print("Starting update_country_peril.py.py")
print("Importing dependencies")

import configparser
import arcpy
import os
import sys
import logging.handlers

from helpers import get_logger

cconf_table = "GLOBAL_EXPOSURE.dbo.COUNTRYCONFIG"

class UpdateCountryPeril:
    __logger = {}

    def __init__(self):
        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        script_file = os.path.basename(__file__)
        formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

        consoleHandler = logging.StreamHandler(sys.stdout)
        consoleHandler.setLevel(logging.DEBUG)
        consoleHandler.setFormatter(formatter)

        fileHandler = logging.handlers.RotatingFileHandler(filename="update_country_peril.log",maxBytes=1024000, backupCount=10, mode="a")
        fileHandler.setLevel(logging.INFO)
        fileHandler.setFormatter(formatter)

        self.__logger.addHandler(consoleHandler)
        self.__logger.addHandler(fileHandler)

        self.__logger.info("Start")
        self.__logger.info(arcpy.GetMessages())

        config = self.read_config_ini()

        try:
            #TODO:Create the connection on the fly? db server, user password... this will  fail in prod & preprod or run on db servers?
            #workspace = r"C:\Users\S01397\Code\arcgisserver\connections\STAGING_GLOBAL_EXPOSURE_as_PNP_USER.sde"
            workspace = 'D:\\arcgisserver\\connections\\STAGING_GLOBAL_EXPOSURE_as_PNP_USER.sde'
            
            target_path = os.path.join(workspace, cconf_table)
            self.__logger.info("Target table: {}".format(target_path))

            for config_key_arg in config:
                if config_key_arg == 'DEFAULT':
                    continue
            
                perils = config[config_key_arg]["perils"]
                countries_iso2_codes = config[config_key_arg]["countries_iso2_codes"]
                add = config[config_key_arg]["include"]

                if add.lower() == "true":
                    self.AddPerils(target_path, perils, countries_iso2_codes)                        
                else:
                    self.RemovePerils(target_path, perils, countries_iso2_codes)

        except Exception as e:
            self.__logger.error(e)

    def AddPerils(self, target_path, perils, countries_iso2_codes):
        try:
            incoming_perils_array = perils.split(",")

            for country in countries_iso2_codes.split(","):
                fields = ['ISO2', 'Perils']
                with arcpy.da.UpdateCursor(in_table=target_path, field_names=fields, where_clause="ISO2 = '{0}'".format(country)) as cursor: 
                    for row in cursor:
                        current_perils_array = row[1].split(",")
                        new_perils_string = self.combine_perils(incoming_perils_array, current_perils_array)
                        self.__logger.info(f"Updating {country} perils to add {new_perils_string}")  
                        row[1] = new_perils_string
                        cursor.updateRow(row)    
   
     
        except Exception as e:
            self.__logger.error(f"AddPerils error - {e}")

    def combine_perils(self, incoming_perils_array, current_perils_array):
        new_perils_array = list(set(incoming_perils_array + current_perils_array))
        new_perils_string = ','.join(new_perils_array)
        return new_perils_string

    def RemovePerils(self, target_path, perils, countries_iso2_codes):
        try:
            perils_to_remove_array = perils.split(",")

            for country in countries_iso2_codes.split(","):
                        
                fields = ['ISO2', 'Perils']
                with arcpy.da.UpdateCursor(in_table=target_path, field_names=fields, where_clause="ISO2 = '{0}'".format(country)) as cursor: 
                    for row in cursor:
                        current_perils_array = row[1].split(",")
                        new_perils_string = self.remove_perils(perils_to_remove_array, current_perils_array)
                        self.__logger.info(f"Updating {country} perils to  {new_perils_string}")    
                        row[1] = new_perils_string
                        cursor.updateRow(row)      
 
                                    
        except Exception as e:
            self.__logger.error(f"Remove error - {e}")

    def remove_perils(self, perils_to_remove_array, current_perils_array):
        new_perils_array = list(set(current_perils_array) - set(perils_to_remove_array))
        new_perils_string = ','.join(new_perils_array)
        return new_perils_string

    def read_config_ini(self):
        path = os.path.dirname(os.path.realpath(__file__))
        config_ini_path = os.path.join(path, "config\config.ini")
        config = configparser.ConfigParser()
        # config.optionxform = str  # Case sensitive config values
        config.read(config_ini_path)
        return config

if __name__ == "__main__":
    processor = UpdateCountryPeril()