

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
     
    # For countries in the updates table, add the perils e.g GLOBAL_MORATORIUMS
    try:
         
        workspace = 'D:\\arcgisserver\\connections\\PREPROD_GLOBAL_EXPOSURE_as_PNP_USER.sde'
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
    


    # Loop through the countries table and find all countries without GLOBAL_MORATORIUMS and add to the perils
"""     try: 
        #workspace = 'D:\\arcgisserver\\connections\\PREPROD_GLOBAL_EXPOSURE_as_PNP_USER.sde'
        workspace = 'C:\\Users\\S01397\\Code\\arcgisserver\\connections\\STAGING_GLOBAL_EXPOSURE_as_PNP_USER.sde'

        cconf_table = "GLOBAL_EXPOSURE.dbo.COUNTRYCONFIG_TEST" 
        target_path = os.path.join(workspace, cconf_table)
        logger.info("Target table: {}".format(target_path))

        countries_to_update = []

        #Check if GLOBAL_MORATORIUMS exists
        search_fields= ['ISO2','Perils']
        with arcpy.da.SearchCursor(in_table=target_path, field_names=search_fields) as cur:
            for row in cur: 
                if 'GLOBAL_MORATORIUMS' not in row[1]:
                    logger.info("Country {0} does not have GLOBAL_MORATORIUMS".format(row[0]))
                    countries_to_update.append(row[0])

        for country in countries_to_update:
            with arcpy.da.UpdateCursor(in_table=target_path, field_names=search_fields, where_clause="ISO2 = '{0}'".format(country)) as cursor: 
                for row in cursor:
                    logger.info("Adding GLOBAL_MORATORIUMS to country: {0} ".format(country))
                    row[1] +=",GLOBAL_MORATORIUMS"
                    cursor.updateRow(row)
                    
                del cursor

        logger.info("END")

    except Exception as e:

        logger.error(e)
     """