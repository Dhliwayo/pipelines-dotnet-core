import arcpy
from utils import helpers

#The following are the conditions under which Arcpy can be authorised outside the application
#   Sign me in automatically is checked when signing in to ArcGIS Pro.
#   ArcGIS Pro is currently open.
#   ArcGIS Pro has been authorized to work offline.
#   ArcGIS Pro is configured with a Concurrent Use license and at least one license is available on ArcGIS License Manager.
def activate_license():
    try:
        logger = helpers.get_logger("LicenseChecker.py", "./initialiseLisense.log")
        arcpro_version = arcpy.GetInstallInfo()
        version = arcpro_version["Version"]
        licenseLevel = arcpro_version["LicenseLevel"]
        productName = arcpro_version["ProductName"]
        licenseType = arcpro_version["LicenseType"]

        logger.fatal(f"License information {version}, {licenseLevel}, {productName}, {licenseType}")

        # do something cool with arcpy
    except Exception as e:
        logger.fatal(f"ArcGIS Pro 3.0 or greater required to run this tool {e}")
        raise Exception
    
