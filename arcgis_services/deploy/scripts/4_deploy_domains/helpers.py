import logging
import logging.handlers
import sys


import arcpy


def get_logger(logger_name: str, log_file: str):
    """
    Create a logger object configure to write to console and also a supplied log file
    
    :param logger_name: Name logger can be referenced by
    :param log_file: path to log_file, will be created if doesn't exist, will be appended to if does
    :returns: logging.Logger object
    """
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(logger_name))

    consoleHandler = logging.StreamHandler(sys.stdout)
    consoleHandler.setLevel(logging.DEBUG)
    consoleHandler.setFormatter(formatter)

    fileHandler = logging.handlers.RotatingFileHandler(filename=log_file, maxBytes=1024000, backupCount=10, mode="a")
    fileHandler.setLevel(logging.INFO)
    fileHandler.setFormatter(formatter)

    logger.addHandler(consoleHandler)
    logger.addHandler(fileHandler)

    return logger


def create_sde_connection_file(username: str, password: str, directory: str, server: str, database: str):
    """
    Create a local .sde connection file which will be cleaned up by garbage collection at runtime end
    
    For a temporary directory pass in temp_dir = tempfile.TemporaryDirectory().name
    
    :param username: account username to form connection
    :param password: account password to form connection
    :param directory: directory to store the .sde in
    :param server: eg. lwwipiv3.opd.ads.uk.rsa-ins.com
    :param database: eg. GRA_REPOSITORY
    :return: string path to .sde file
    """
    filename = server+"_"+database+".sde"
    filepath = arcpy.CreateDatabaseConnection_management(
        out_folder_path=directory,
        out_name=filename,
        database_platform="SQL_SERVER",
        instance=server,
        username=username,
        password=password,
        save_user_pass="SAVE_USERNAME",
        database=database,
    )

    return str(filepath)
