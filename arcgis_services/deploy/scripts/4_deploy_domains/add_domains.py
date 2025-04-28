# RSA 2022

# TODO:
# Read from secret!

# Notes
#---------
# This can run from the built machine


# Functions 


# SQL clause functions 

def build_clause(field: str, value: str) -> str:
    """ 
    """
    clause = "{0} = '{1}'".format(field, value)

    return clause


def concat_clauses(clauses: list, andor: str) -> str:
    """ 
    Build arcpy-friendly where clause
    
    """
    andor.strip()
    andor = andor.upper()
    andor = " {} ".format(andor) # pad and/or
    big_clause = andor.join(clauses)

    return big_clause


def where_from_iterables(fields: tuple, values: tuple) -> str:
    """
    Creates a where clause 
    
    """

    lenf = len(fields)
    lenv = len(values)

    if lenf != lenv:

        message  = "Different number of fields ({0}) and values ({1})".format(lenf, lenv)
        raise ValueError("Different number of fields and values")
    
    clauses = []
    
    for pair in zip(fields, values):

        field = pair[0]
        value = pair[1]
        field_val_clause = build_clause(field, value)
        clauses.append(field_val_clause)
    
    out_clause = concat_clauses(clauses, "AND")

    return out_clause


# arcpy search/update logic 

def count_where(in_table: str, fields: list, where: str) -> int:
    """ 
    There should be constraints in the database to enforce 
    uniqueness, etc. 
    
    """
    n = 0 
    with SearchCursor(in_table, fields, where_clause=where) as cursor:
        for row in cursor:
            n+=1
    
    del cursor 

    return n


def insert_row(row: tuple, fields: tuple, target_layer: object) -> bool:

    cursor = InsertCursor(target_layer, fields)

    cursor.insertRow(row)

    logger.info("Inserted {0}".format(row))

    del cursor 
    # del target_layer 

    return True


def count_then_insert(row: tuple, fields: list, target_path: object, target_layer: object) -> str:
    """
    Check whether inserted row values are unique

    If they are unique, inserts them
    
    """

    logger.info("Executing count_then_insert: {}".format(row))

    try: 

        # target_layer = arcpy.management.MakeTableView(target_path, "target_layer", workspace=workspace)

        # Make a WHERE clause 

        where = where_from_iterables(fields, row)

        # Search using SearchCursor

        existing_count = count_where(target_path, fields, where)

        if existing_count > 0: 

            logger.info("Skipping insert WHERE {1}. This row already exists.".format(existing_count, where))

        else: 
        
            insert_row(row, fields, target_layer)

    except Exception as e:

        logger.error(e)

    finally: 

        if target_layer:
            
            del target_layer

    return target_path


# Logic 

if __name__ == "__main__":

    # Imports

    print("Starting")
    print("Importing dependencies")

    import arcpy
    import configparser
    import logging
    import logging.handlers
    import os
    import sys
    from getpass import getpass
    import tempfile

    from arcpy.da import SearchCursor, InsertCursor
    
    from helpers import get_logger
    from helpers import create_sde_connection_file

    logger = get_logger("Add domain entries.py", "./app.log")

    try: 
        config = configparser.ConfigParser()
        config_ini_path = "./config.ini"
        config.read(config_ini_path)
       
        for key in config:
            if key == 'DEFAULT':
                continue
        
            logger.info("Executing for config key " + key) 

            toolbox_path = config[key]["toolbox_path"]
            username = config[key]["username"]
            server = config[key]["server"]
            database = config[key]["database"]
            domain_type = config[key]["domain_type"]
            codes = config[key]["codes"].split(",")
            values = config[key]["values"].split(",")

            password = getpass(prompt='Password for user '+username+': ')
            
            temp_dir = tempfile.TemporaryDirectory()  # this needs creating outside the function so that the garbage collector doesnt delete it when function context closes
            workspace = create_sde_connection_file(username, password, temp_dir.name, server, database)

            domain_name = "GLOBAL_EXPOSURE.dbo.DOMAINLOOKUPS"
            domain_path = os.path.join(workspace, domain_name)
            logger.info("DOMAINLOOOKUPS path: {0}".format(domain_path))

            lookup_name = "GLOBAL_EXPOSURE.dbo.Lookup_"+domain_type

            lookup_path = os.path.join(workspace, lookup_name)
            logger.info("Lookup path: {0}".format(lookup_path))
            
            # confirm lookup path, built with config domain_type, is valid
            # this will throw an informative error if the lookup path does not exist
            arcpy.management.MakeTableView(lookup_path, "confirm_lookup_path_check_"+key, workspace=workspace)
       
            # dbo.DOMAINUPDATES

            domainlookups_layer = arcpy.management.MakeTableView(domain_path, "target_layer"+key, workspace=workspace)

            domain_fields = ["DomainName", "Code", "Value"]
            for entry in zip(codes, values):
                logger.info("Adding row: "+entry[0]+", "+entry[1])
                domain_entry = [domain_type]+list(entry)  # we need 3 fields to get unique value in domain
                count_then_insert(domain_entry, domain_fields, domain_path, domainlookups_layer)
            
            del domainlookups_layer

            # 3. Execute PnP domain update model 

            logger.info("Executing PnP domain update model...") 
            try: 
                toolbox = arcpy.AddToolbox(toolbox_path)

                toolbox.CreateDomains(
                    lookupTable=domain_path,
                    pnpWorkspace=workspace
                )

                logger.info("Esri script tool output: \n\n{}\n".format(arcpy.GetMessages()))

            except Exception as e:

                logger.error(e)

            # Update lookup table 
            logger.info("Updating dbo.Lookup_* tables...")
            try: 
                lookup_layer = arcpy.management.MakeTableView(lookup_path, "lookup_layer"+key, workspace=workspace)
                
                lookup_fields = ["Code", "Value"]
                for entry in zip(codes, values):
                    logger.info("Adding row: "+entry[0]+", "+entry[1])
                    count_then_insert(list(entry), lookup_fields, lookup_path, lookup_layer)
                
                del lookup_layer

            except Exception as e:

                logger.error(e)
        
    except Exception as e:

        logger.error(e)
    
    input("Press return to exit")
        
