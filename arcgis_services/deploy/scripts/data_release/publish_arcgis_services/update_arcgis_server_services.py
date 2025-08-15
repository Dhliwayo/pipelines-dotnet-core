import os
import shutil
import arcpy
import arcgisscripting
import requests
import xml.dom.minidom as DOM
import json
import logging

from utilities import temporary_files


def publish_to_arcgis_server(logger: logging.Logger, outputDirectory: str, mapFile: str, serverURL: str, username: str, password: str, releaseName: str, serviceName: str, serviceFolder=''):
    """
    Publish Map Service - July 2023 - Author: Kieran Heapy
    This function publishes a mapx file to arcgis server using a connection file to the server, and a destination service name and folder

    Note: always overwrites, if serverFolder/serviceName is new, just publishes
    Note: always trys to reference data, will error if copying

    example from: https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/mapservicedraft-class.htm#GUID-89320827-156F-4377-A179-8CC53976CA17
    
    :logger: A logger object, can be constructed with release_tools.logging.get_logger()
    :outputDirectory: path to storage for sddraft and sd (service definition)
    :mapFile: path to .mapx file to be published
    :serverURL: url to server manager, required for collecting existing service properties
    :username: login credentials to server manager, required for collecting existing service properties
    :password: login credentials to server manager, required for collecting existing service properties
    :releaseName: attached to the created blank aprx project so it is pulled through to the published properties on server
    :serviceName: name that will be given to the arcgis map service
    :serviceFolder: optional folder that service will be stored in on server
    :return: True if successful
    """
    if not os.path.exists(outputDirectory):
        logger.error("Output Directory does not exist")
        raise Exception("Output Directory does not exist")

    if serverURL[-1] != "/":
        logger.error("Server URL must end in trailing slash")
        raise Exception("Server URL must end in trailing slash")

    #Set service definition file paths
    sddraft_path = os.path.join(outputDirectory, serviceName + ".sddraft")
    sd_path = os.path.join(outputDirectory, serviceName + ".sd")

    if os.path.exists(sd_path):
        logger.info("Overwriting existing Service Draft")
        os.remove(sd_path)

    # Open .mapx file 
    project_file = __create_blank_project(releaseName)
    aprx = arcpy.mp.ArcGISProject(project_file)
    aprx.importDocument(mapFile)
    aprx.save()

    map = aprx.listMaps('*')[0]

    # Create .ags connection file to be used when creating service draft
    ags_filename = 'ConnectionFile.ags'
    ags_filepath = os.path.join(outputDirectory, ags_filename)
    arcgisscripting._createGISServerConnectionFile(
        "ADMINISTER_GIS_SERVICES", 
        outputDirectory, 
        ags_filename, 
        serverURL, 
        "ARCGIS_SERVER", 
        False, 
        outputDirectory, 
        username, 
        password
    )

    # Create MapServiceDraft, set folder properties, allow overwriting of existing service and use data registered to the server
    service_draft = arcpy.sharing.CreateSharingDraft("STANDALONE_SERVER", "MAP_SERVICE", serviceName, map)
    service_draft.targetServer = ags_filepath
    service_draft.serverFolder = serviceFolder
    service_draft.overwriteExistingService = True
    service_draft.copyDataToServer = False

    logger.info("Creating Service Definition Draft...")
    service_draft.exportToSDDraft(sddraft_path)

    # TODO: allow overwriting of summary/desc metadata
    logger.info("Setup service properties...")
    properties = __get_service_properties(serverURL, username, password, serviceFolder, serviceName)
    if 'serviceName' not in properties:
        # didn't find a service to copy properties from so use defaults
        properties = {
            'minInstancesPerNode': 1,
            'maxInstancesPerNode': 2,
            'properties': {
                'maxRecordCount': 2000,
                'schemaLockingEnabled': 'true',
            },
        }
        
    logger.info("Updating Service Definition Draft properties...")
    __update_draft_service_properties(properties, sddraft_path)

    logger.info("Staging Service Definition...")
    arcpy.StageService_server(sddraft_path, sd_path)
    warnings = arcpy.GetMessages(1)

    # badDataSource = '24011'
    # if badDataSource in warnings:
    #     logger.error("Layer's data source is not registered with the server")
    #     raise Exception("Layer's data source is not registered with the server")

    logger.info("-------------------------------------")
    logger.info(warnings)
    logger.info("-------------------------------------")
    logger.info("Please review the warnings, if none/none of concern...")
    input("...press Enter to continue...")

    logger.info("Uploading Service Definition to server...")
    arcpy.UploadServiceDefinition_server(sd_path, ags_filepath)

    logger.info("Successfully Uploaded service.")

    #TODO: cleanup temporary project
    # del service_draft, map, aprx
    # os.remove(project_file)
    # os.rmdir(temp_dir)

    return True


def __update_draft_service_properties(properties: dict, sddraft_path: str):
    """
    :param properties: the result of __get_service_properties()
    :param sddraft_path: path to an existing service definition draft which will be updated
    """
    #Change the service properties of the sddraft 
    doc = DOM.parse(sddraft_path)  # parse xml
    for key in doc.getElementsByTagName('Key'):
        k = key.firstChild.data
        v = key.nextSibling.firstChild
        if k == 'MinInstances':
            v.data =  properties['minInstancesPerNode']
        if k == 'MaxInstances':
            v.data =  properties['maxInstancesPerNode']
        if k == 'maxRecordCount':
            v.data = properties['properties']['maxRecordCount']
        if k == 'provider':
            v.data = 'ArcObjects11' # Dedicated Instance
        if k == 'schemaLockingEnabled':
            v.data = properties['properties']['schemaLockingEnabled']
         
    # overwrite xml in sddraft
    with open(sddraft_path, 'w') as fp:
        doc.writexml(fp)

    return True


def __get_service_properties(serverURL: str, username: str, password: str, serviceFolder: str, serviceName: str):
    """
    Collect service properties from server for service at serviceFolder/serviceName
    
    :serverURL: url to server manager
    :username: login credentials to server manager
    :password: login credentials to server manager
    :serviceName: name that will be given to the arcgis map service
    :serviceFolder: optional folder that service will be stored in on server
    """
    # we get an unverified https request warning, ignore that
    requests.packages.urllib3.disable_warnings()

    # Generate a token to use in request to get service properties
    token = __get_server_token(serverURL, username, password)
    
    # Use the token to access the service properties to add back to the new sddraft
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    servicePath = serviceName if serviceFolder=='' else serviceFolder+"/"+serviceName
    url = serverURL + 'services/' + servicePath + '.MapServer'
    
    payload = {'f':'json', 'token':token}

    return json.loads(requests.post(url, data=payload, headers=headers).content)


def __get_server_token(serverURL: str, username: str, password: str):
    payload = {'username': username, 'password': password, 'client': 'requestip','expiration': '60', 'request': 'gettoken', 'f': 'json'}
    token_url = serverURL + "generateToken"
    response = json.loads(requests.post(token_url, data=payload, verify=False).content)

    if 'token' in response:
        return response.get('token', None)

    raise Exception("Unable to generate token, check username/password credentials")


def __create_blank_project(releaseName: str):
    """
    We build a new blank project by copying an entire template folder structure to a new location
    
    :param releaseName: the project will be renamed to this
    :return: path to temporary blank .aprx file built from template folder
    """
    template_dir = __get_arcgis_pro_project_template()
    temp_dir = temporary_files.get_temporary_directory()

    dest = shutil.copytree(template_dir, os.path.join(temp_dir, releaseName))

    project_file = os.path.join(dest, releaseName+'.aprx')

    # we do this copy to effectively rename the aprx so that we release from the desired releaseName
    aprx = arcpy.mp.ArcGISProject(os.path.join(dest, 'template.aprx'))
    aprx.saveACopy(project_file)
    del aprx  # there's no close on a project object?

    return project_file


def __get_arcgis_pro_project_template():
    """
    We have to use an entire project directory as our template
    to avoid issues with the import Log being created in the wrong place (even if we change the aprx.homeFolder attr)

    :return: path to blank template folder for current arcgis Pro Version
    """
    pro_version = arcpy.GetInstallInfo()['Version']
    pro_version_string = pro_version.replace(".", "")[:2]  # eg 3.0.3 -> 30
    template_name = f"template_{pro_version_string}"
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "arcgis_templates", template_name)

    if not os.path.exists(template_dir):
        raise Exception("Template directory does not exist for ArcGIS Pro version: " + pro_version)

    if not os.path.exists(os.path.join(template_dir, 'template.aprx')):
        raise Exception("Template directory does not contain template.aprx for ArcGIS Pro version: " + pro_version)

    return template_dir
