import os
import sys
import requests
import logging
import logging.handlers

server_services_directory = 'https://lwukwvri53.opd.ads.uk.rsa-ins.com/arcgis/rest/services?f=pjson'
#server_services_directory = 'https://lwukwvri52.opd.ads.uk.rsa-ins.com/arcgis/rest/services?f=pjson'
#server_services_directory = 'https://lwukwvpi255.opd.ads.uk.rsa-ins.com/arcgis/rest/services?f=pjson'
#server_services_directory = 'https://www.google.com' #Works fine
#server_services_directory = 'https://rsagroup.csod.com' #Works fine

def test_rest_api_call():
    try:
        headers = {
        "Accept": "application/json"
        }
        response = requests.get(
            url=server_services_directory,
            verify=False)
        logger.info(f'Succesful call to ArcGIS server API: {response}')
        logger.info(f'ArcGIS server API response: {response.content}')
    except  requests.exceptions.ConnectionError as e:
        logger.info(f'Failed to make REST call: {e.args[0]}')
    except ConnectionResetError as e:
        logger.info(f'Failed to make REST call: {e.message}')
    except Exception as e:
        logger.info(f'Failed to make REST call: {e.message}')

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    script_file = os.path.basename(__file__)
    formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)

    fileHandler = logging.handlers.RotatingFileHandler(filename="rest-api-tests.log",maxBytes=1024000, backupCount=10, mode="a")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    
    try:
        logger.info("Start test rest api call")
        test_rest_api_call()

    except Exception as e:
        logger.error(e)
        