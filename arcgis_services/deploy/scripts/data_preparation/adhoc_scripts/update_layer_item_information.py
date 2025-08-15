import json #httplib, urllib
import sys
import getpass
import os
import sys
import requests
import logging
import logging.handlers

#https://developers.arcgis.com/rest/services-reference/online/add-to-definition-feature-layer/
#https://<adminservicecatalog-url>/services/<serviceName>/FeatureServer/<layerId>/addToDefinition
#editSvcURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/rest/admin/services/georisk/insured_locations_only/FeatureServer/0/addToDefinition"
#https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/rest/services/tests/Perils/MapServer/32
editSvcURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/admin/services/tests/Perils.MapServer/iteminfo/upload"

#https://developers.arcgis.com/rest/enterprise-administration/server/edititeminfo/

#https://developers.arcgis.com/rest/services-reference/online/update-definition-feature-layer/#GUID-FC672B01-6C50-4E8B-B736-BF008603E402

serviceURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/admin/services/tests/Perils.MapServer/iteminfo" 
#serviceURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/rest/admin/services/georisk/insured_locations_only/FeatureServer/0"
#"https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/rest/services/georisk/insured_locations_only/FeatureServer/0"
#serviceURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/rest/services/tests/Perils/MapServer/44/iteminfo"


#editSvcURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/admin/services/tests/Perils.MapServer/edit"
# Token URL is typically http://server[:port]/arcgis/admin/generateToken
#tokenURL = "/arcgis/admin/generateToken"
tokenURL = "https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/admin/generateToken"

# Defines the entry point into the script
def main(argv=None):
    logger.info("This tool is a sample script that resets the minimum and maximum instances allowed for a service.")

    username = 'siteadmin'
    password = 'password2'

    # Get a token
    token = getToken(username, password)
    if token == "":
        logger.info( "Could not generate a token with the username and password provided."  )  
        return   
    
    # This request only needs the token and the response formatting parameter 
    #params = urllib.urlencode({'token': token, 'f': 'json'})
    params = {'token': token, 'f': 'json'}
    
    #headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    headers = {"Content-type": "application/json", "Accept": "text/plain"}
    
    #Get current content of layer
    response = requests.post(url=serviceURL, params=params, headers=headers,verify=False)
    
    # Read response
    if (response.status_code != 200):
        logger.info(  "Could not read service information.")
        return
    else:
        data = response.content
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            logger.info(  "Error when reading service information. " + str(data))
        else:
            logger.info(  "Service information read successfully. Now changing properties...")

        # Deserialize response into Python object
        dataObj = json.loads(data)

        dataObj["name"] = 'GLOBAL_FLOOD_OCEANIA'

        # Serialize back into JSON
        updatedSvcJson = json.dumps(dataObj)

        params = {'token': token, 'f': 'json', 'service': updatedSvcJson}

        #httpConn.request("POST", editSvcURL, params, headers)
        editResponse = requests.post(url=editSvcURL, params=params, headers=headers,verify=False)
        
        # Read service edit response
        if (editResponse.status_code != 200):
            logger.info(  "Error while executing edit.")
            return
        else:
            editData = editResponse.content
            
            # Check that data returned is not an error object
            if not assertJsonSuccess(editData):
                logger.info(  "Error returned while editing service" + str(editData) )       
            else:
                logger.info(  "Service edited successfully.")
        return

# A function to generate a token given username, password and the adminURL.

def getToken(username, password):
   
    #params = urllib.urlencode({'username': username, 'password': password, 'client': 'requestip', 'f': 'json'})
    params = {'username': username, 'password': password, 'client': 'requestip', 'f': 'json', "expiration"  : '180'}
    
    # Connect to URL and post parameters
    #httpConn = httplib.HTTPConnection(serverName, serverPort)
    #httpConn.request("POST", tokenURL, params, headers)
    requests.packages.urllib3.disable_warnings()
    response = requests.post(url=tokenURL, data=params, verify=False)
    
    # Read response
    if (response.status_code != 200):
        logger.info(  "Error while fetching tokens from admin URL. Please check the URL and try again.")
        return
    else:
        data = response.content
        
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):            
            return
        
        # Extract the token from it
        token = json.loads(data)        
        return token['token']            
        

# A function that checks that the input JSON object 
#  is not an error object.
    
def assertJsonSuccess(data):
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        logger.info(  "Error: JSON object returns an error. " + str(obj))
        return False
    else:
        return True
    
        
# Script start 
if __name__ == "__main__":

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    script_file = os.path.basename(__file__)
    formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)

    fileHandler = logging.handlers.RotatingFileHandler(filename="update_layer_definition.log",maxBytes=1024000, backupCount=10, mode="a")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)
    
    sys.exit(main(sys.argv[1:]))