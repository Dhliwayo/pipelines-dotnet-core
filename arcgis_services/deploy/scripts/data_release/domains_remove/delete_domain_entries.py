import os
import configparser
from getpass import getpass
from pathlib import Path
import tempfile

import arcpy

from utils import helpers


def read_config_ini():
    path = os.path.dirname(os.path.realpath(__file__))
    config_ini_path = os.path.join(path, "config\config.ini")
    config = configparser.ConfigParser()
    # config.optionxform = str  # Case sensitive config values
    config.read(config_ini_path)
    return config

def delete_row_matching_values(fields: list, values: list, table: str, workspace: str):
    """
    Delete all rows in a given table where the values for fields are present
    if no row is found that matches all values nothing will be done
    
    :param fields: list of field names that values correspond to
    :param values: list of values for row to be deleted, all rows macthing these values will be deleted
    :param table: string connection path to table
    :param workspace: string .sde connection file
    :returns: True if successful
    """
    # update cursor takes a table view, not a connection path
    table_view = arcpy.management.MakeTableView(table, "temp_table_view", workspace=workspace)

    #logger.info(table)
    #logger.info(fields)

    with arcpy.da.UpdateCursor(table_view, fields) as cursor:
        for row in cursor:
            if list(row) == values:
                cursor.deleteRow()

    arcpy.Delete_management(table_view)

    return True


logger = helpers.get_logger("Delete domain entries.py", "./delete_domain_entries.log")

try:
    config = read_config_ini()

    if(len(config.sections()) == 0):
        logger.warning("No sections detected in add domain config.ini") 

    current_working_directory  = Path(__file__).parent.absolute()

    for key in config:
        if key == 'DEFAULT':
            continue

        logger.info("Executing for config key " + key) 

        toolbox_path = os.path.join(current_working_directory,config[key]["toolbox_path"])
        domain_type = config[key]["domain_type"]
        codes = config[key]["codes"].split(",")
        values = config[key]["values"].split(",")

        workspace = 'D:\\arcgisserver\\connections\\FINT_GLOBAL_EXPOSURE_as_PNP_USER.sde'
        #workspace = 'C:\\Users\\S01397\\Code\\arcgisserver\\connections\\STAGING_GLOBAL_EXPOSURE_as_PNP_USER.sde'

        domain_name = "GLOBAL_EXPOSURE.dbo.DOMAINLOOKUPS"
        domain_path = os.path.join(workspace, domain_name)
        logger.info("DOMAINLOOOKUPS path: {0}".format(domain_path))

        lookup_name = "GLOBAL_EXPOSURE.dbo.Lookup_"+domain_type

        lookup_path = os.path.join(workspace, lookup_name)
        logger.info("Lookup path: {0}".format(lookup_path))
        
        # confirm lookup path, built with config domain_type, is valid
        # this will throw an informative error if the lookup path does not exist
        arcpy.management.MakeTableView(lookup_path, "confirm_lookup_path_check", workspace=workspace)

        # remove lookup entries
        sqlConn = arcpy.ArcSDESQLExecute(workspace)

        codes_string = "('" + "','".join(codes) + "')"

        sqlQuery = "DELETE FROM "+lookup_name+" WHERE Code IN "+codes_string
        sqlConn.execute(sqlQuery)


        # remove domains
        logger.info("Executing PnP domain update model...") 

        domain_fields = ["DomainName", "Code", "Value"]
        for entry in zip(codes, values):
            logger.info("Deleting row: "+entry[0]+", "+entry[1])
            domain_entry = [domain_type]+list(entry)  # we need 3 fields to get unique value in domain
            delete_row_matching_values(domain_fields, domain_entry, domain_path, workspace)

        # rebuild domains
        logger.info("Rebuilding Domains") 
        toolbox = arcpy.AddToolbox(toolbox_path)

        toolbox.CreateDomains(
            lookupTable=domain_path,
            pnpWorkspace=workspace
        )

        logger.info("Esri script tool output: \n\n{}\n".format(arcpy.GetMessages()))
except Exception as e:

    logger.error(e)
