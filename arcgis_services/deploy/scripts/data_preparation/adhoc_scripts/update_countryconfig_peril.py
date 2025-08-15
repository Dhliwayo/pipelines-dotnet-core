

if __name__ == "__main__":

    # Imports

    print("Starting")
    print("Importing dependencies")

    import arcpy
    import os
    import sys
    
    from helpers import get_logger

    from arcpy.da import SearchCursor, InsertCursor

    logger = get_logger("update_countryconfig.py", "./app.log")
    
    # config.ini handler 
     
    try:
         
        workspace = 'D:\\arcgisserver\\connections\\STAGING_GLOBAL_EXPOSURE_as_PNP_USER.sde'
        cconf_table = "GLOBAL_EXPOSURE.dbo.COUNTRYCONFIG" 
        
        #For testing, uncomment above line and comment this
        #workspace = 'C:\\Users\\S01397\\Code\\arcgisserver\\connections\\STAGING_GLOBAL_EXPOSURE_as_PNP_USER.sde'
        #cconf_table = "GLOBAL_EXPOSURE.dbo.COUNTRYCONFIG_TEST"

        target_path = os.path.join(workspace, cconf_table)
        logger.info("Target table: {}".format(target_path))

        updates = {
            'GB': 'GLOBAL_MORATORIUMS',
            'GG': 'GLOBAL_MORATORIUMS',
            'IM': 'GLOBAL_MORATORIUMS',
            'JE': 'GLOBAL_MORATORIUMS',
        }

        for country in updates:
            
            logger.info("Checking {0}".format(country))
            
            fields = ['ISO3', 'Perils']
            with arcpy.da.UpdateCursor(in_table=target_path, field_names=fields, where_clause="ISO2 = '{0}'".format(country)) as cursor: 
                for row in cursor:
                    if updates[country] not in row[1]:
                        logger.info("Updating {0} to add {1}".format(country, updates[country]))
                        row[1] +=","+updates[country]
                        cursor.updateRow(row)
                    
                del cursor
        
        logger.info("END")

    except Exception as e:
        logger.error(e)
    
