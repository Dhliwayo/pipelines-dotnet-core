
if __name__ == "__main__":

    # Imports

    print("Starting")
    print("Importing dependencies")

    import arcpy
    import os
    from arcpy import env
    
    from helpers import get_logger

    logger = get_logger("copy_rasters_into_gdb.py", "./copy_rasters_into_gdb.log")
    
    try:
        source_workspace = r"C:\Users\S01397\Code\Data\PERILS_B.gdb"
        target_workspace = env.workspace = r"C:\Users\S01397\Code\Data\PropertyPhaseII\PropertyPhase_II.gdb" 
        
        #layers = 'UK_COUNTRY,UK_ARSON_V2'
        layers = 'UK_AFFLUENCE,UK_ARSON_V2,UK_COUNTRY,UK_FIRE_AFA_POLICY,UK_FREEZE,UK_HOUSE_AGE_BAND,UK_HOUSEHOLD_INCOME,UK_IMPACT,UK_STORM,UK_SUBSIDENCE_V2,UK_THEFT,UK_URBANICITY,UK_VANDALISM,UK_WATER_HARDNESS'

        for layer in layers.split(','):
            source_path = os.path.join(source_workspace, layer)
            target_path = os.path.join(target_workspace, layer)

            #TODO: Check if we need to overwrite without a warning!
            arcpy.env.overwriteOutput = True

            logger.info(arcpy.GetMessages())

            if arcpy.Exists(target_path):
                logger.info(f"Deleting existing file target {target_path}....")
                arcpy.Delete_management(target_path)
            
            desc = arcpy.Describe(source_path)
            
            if hasattr(desc, "RasterDataset"):
                logger.info(f"Copying raster {layer}....")
                arcpy.CopyRaster_management(source_path, target_path)
                logger.info(f"Finished copying {layer}....")
            else:
                logger.info(f"Copying feature class {layer}....")
                arcpy.Copy_management(source_path, target_path)
                logger.info(f"Finished copying {layer}....")
        logger.info("END")
    except Exception as e:
        logger.info(arcpy.GetMessages())
        logger.error(e)
        
