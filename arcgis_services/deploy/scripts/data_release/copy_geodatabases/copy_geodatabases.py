# RSA 2025 

# Copies all the geodatabases from the source to target as specified in the config file, if the update_in_release is set to True

# Imports 

import arcpy 
import configparser
import logging
import logging.handlers
import os 
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock



class CopyGeodatabases:
    __logger = {}
    __log_lock = Lock()
    
    def __init__(self, max_workers=None):

        self.__logger = logging.getLogger(__name__)
        self.__logger.setLevel(logging.DEBUG)
        script_file = os.path.basename(__file__)
        formatter = logging.Formatter('%(asctime)s - {} - %(levelname)s - %(message)s'.format(script_file))

        # Configure handlers once to avoid duplicated logs if re-instantiated
        if not self.__logger.handlers:
            consoleHandler = logging.StreamHandler(sys.stdout)
            consoleHandler.setLevel(logging.DEBUG)
            consoleHandler.setFormatter(formatter)

            log_dir = os.path.dirname(os.path.realpath(__file__))
            log_path = os.path.join(log_dir, "copy_geodatabases.log")
            fileHandler = logging.handlers.RotatingFileHandler(filename=log_path, maxBytes=1024000, backupCount=10, mode="a")
            fileHandler.setLevel(logging.INFO)
            fileHandler.setFormatter(formatter)

            self.__logger.addHandler(consoleHandler)
            self.__logger.addHandler(fileHandler)

        self.__logger.info("Start")

        config = self.read_config_ini()

        # Collect all copy operations to execute
        copy_tasks = []
        for config_key_arg in config:
            if config_key_arg == 'DEFAULT':
                continue
        
            source_gdb = config[config_key_arg]["source_gdb"]
            target_gdb = config[config_key_arg]["target_gdb"]
            try:
                update_in_release = config[config_key_arg]["update_in_release"]
            except KeyError:
                raise KeyError(f"Missing 'update_in_release' for section '{config_key_arg}' in config.ini")

            should_update_gdb = self.set_should_update_value(update_in_release)

            if should_update_gdb:
                copy_tasks.append((config_key_arg, source_gdb, target_gdb))
            else:
                self.__logger.info(config_key_arg + " - Data update for key is set to false and will be ignored") 

        # Execute copy operations in parallel
        if copy_tasks:
            self.__logger.info(f"Executing {len(copy_tasks)} geodatabase copy operations in parallel")
            self.execute_parallel_copies(copy_tasks, max_workers)
        else:
            self.__logger.info("No geodatabase copy operations to execute")

        self.__logger.info("End")

    def set_should_update_value(self, update_in_release):
        if isinstance(update_in_release, bool):
            return update_in_release
        value = str(update_in_release).strip().lower()
        if value in ("true", "1", "yes", "on"):            
            return True
        if value in ("false", "0", "no", "off"):
            return False
        raise ValueError("update_in_release parameter is neither True nor False")


    # Functions 

    def read_config_ini(self):
        path = os.path.dirname(os.path.realpath(__file__))
        config_ini_path = os.path.join(path, "config", "config.ini")
        config = configparser.ConfigParser()
        # config.optionxform = str  # Case sensitive config values
        config.read(config_ini_path)
        return config

    def execute_parallel_copies(self, copy_tasks, max_workers=None):
        """
        Execute geodatabase copy operations in parallel using ThreadPoolExecutor
        
        Args:
            copy_tasks: List of tuples (config_key, source_gdb, target_gdb)
            max_workers: Maximum number of worker threads (None = auto-detect)
        """
        if max_workers is None:
            # Default to number of tasks, but cap at reasonable limit
            max_workers = min(len(copy_tasks), 8)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_task = {
                executor.submit(self.execute_copy_gdb, config_key, source_gdb, target_gdb): 
                (config_key, source_gdb, target_gdb)
                for config_key, source_gdb, target_gdb in copy_tasks
            }
            
            # Process completed tasks
            completed = 0
            failed = []
            
            for future in as_completed(future_to_task):
                config_key, source_gdb, target_gdb = future_to_task[future]
                completed += 1
                
                try:
                    future.result()  # This will raise any exception that occurred
                    with self.__log_lock:
                        self.__logger.info(f"[{completed}/{len(copy_tasks)}] ... finished copying {config_key}: {target_gdb}")
                except Exception as e:
                    failed.append((config_key, source_gdb, target_gdb, str(e)))
                    with self.__log_lock:
                        self.__logger.error(f"[{completed}/{len(copy_tasks)}] FAILED copying {config_key}: {target_gdb}")
            
            # Report summary
            if failed:
                self.__logger.error(f"Failed to copy {len(failed)} out of {len(copy_tasks)} geodatabases:")
                for config_key, source_gdb, target_gdb, error in failed:
                    self.__logger.error(f"  - {config_key}: {error}")
                raise Exception(f"{len(failed)} geodatabase copy operation(s) failed")

    def execute_copy_gdb(self, config_key, source_gdb, target_gdb):
        """ 
        Execute the copying of data with arcpy message capture
        
        Args:
            config_key: Configuration key identifier for logging
            source_gdb: Source geodatabase path
            target_gdb: Target geodatabase path
        """
        try:
            # Clear any previous messages
            arcpy.ClearMessages()
            arcpy.env.overwriteOutput = True

            # Validate inputs
            if not source_gdb:
                raise ValueError("source_gdb is empty")
            if not target_gdb:
                raise ValueError("target_gdb is empty")

            with self.__log_lock:
                self.__logger.info("{0}...copying {1} to {2}".format(config_key, source_gdb, target_gdb))

            # Ensure destination directory exists
            target_parent_dir = os.path.dirname(target_gdb)
            if target_parent_dir and not os.path.exists(target_parent_dir):
                os.makedirs(target_parent_dir, exist_ok=True)

            # If target exists, delete first to avoid copy failures
            if arcpy.Exists(target_gdb):
                with self.__log_lock:
                    self.__logger.info("Target exists. Deleting: {0}".format(target_gdb))
                arcpy.management.Delete(target_gdb)
                
                # Capture and log arcpy messages after delete
                delete_messages = arcpy.GetMessages()
                if delete_messages:
                    with self.__log_lock:
                        self.__logger.info(f"[{config_key}] arcpy Delete messages:\n{delete_messages}")
                arcpy.ClearMessages()

            # Copy the geodatabase
            with self.__log_lock:
                self.__logger.info(f"[{config_key}] Copying geodatabase using arcpy.Copy_management")
            
            arcpy.Copy_management(source_gdb, target_gdb)
            
            # Capture and log all arcpy messages (info, warnings, errors)
            # GetMessages() returns all messages since last ClearMessages()
            copy_messages = arcpy.GetMessages()
            if copy_messages:
                with self.__log_lock:
                    self.__logger.info(f"[{config_key}] arcpy Copy messages:\n{copy_messages}")
            
            # Check for warnings and errors separately (GetMessages with severity parameter)
            warnings = arcpy.GetMessages(1)  # Severity 1 = warnings
            errors = arcpy.GetMessages(2)   # Severity 2 = errors
            
            if warnings:
                with self.__log_lock:
                    self.__logger.warning(f"[{config_key}] arcpy Warnings:\n{warnings}")
            
            if errors:
                with self.__log_lock:
                    self.__logger.error(f"[{config_key}] arcpy Errors:\n{errors}")
                raise Exception(f"arcpy reported errors: {errors}")
            
            # Clear messages after successful operation
            arcpy.ClearMessages()

        except Exception as e:
            # Capture any arcpy messages that might have been generated during the error
            try:
                error_messages = arcpy.GetMessages()
                if error_messages:
                    with self.__log_lock:
                        self.__logger.error(f"[{config_key}] arcpy error messages:\n{error_messages}")
            except:
                pass  # If GetMessages fails, continue with original exception
            
            with self.__log_lock:
                self.__logger.exception("Failed to copy geodatabase from '{0}' to '{1}'".format(source_gdb, target_gdb))
            raise

if __name__ == "__main__":
    processor = CopyGeodatabases()

