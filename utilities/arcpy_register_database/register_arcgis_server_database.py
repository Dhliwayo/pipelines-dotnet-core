"""Utility to register SQL Server databases with ArcGIS Server.

The script reads configuration from ``config/config.ini`` in the same directory. Each
section describes a database to register using existing connection files.
"""

from __future__ import annotations

import configparser
import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import arcpy


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG_PATH = SCRIPT_DIR / "config" / "config.ini"


def _resolve_path(raw_path: Optional[str], base_dir: Path) -> Optional[Path]:
    """Resolve a path, expanding environment variables and making it absolute."""
    if not raw_path:
        return None
    
    expanded = os.path.expandvars(raw_path)
    candidate = Path(expanded)
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def _configure_logging(log_directory: Optional[Path]) -> logging.Logger:
    logger = logging.getLogger("register_arcgis_server_database")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_directory:
        log_directory.mkdir(parents=True, exist_ok=True)
        log_path = log_directory / f"register_arcgis_server_database_{datetime.now():%Y%m%d_%H%M%S}.log"
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _register_database(
    server_conn: Path,
    db_conn_serv: Path,
    db_conn_pub: Optional[Path],
    connection_name: str,
    logger: logging.Logger,
) -> None:
    """Register a SQL Server database with ArcGIS Server.
    
    Args:
        server_conn: Path to ArcGIS Server connection file (.ags)
        db_conn_serv: Path to database connection file as seen by the server (.sde)
        db_conn_pub: Optional path to database connection file as seen by the publisher (.sde)
        connection_name: Name for the registered database connection
        logger: Logger instance for output
    """
    # Verify connection files exist
    if not server_conn.exists():
        raise FileNotFoundError(f"Server connection file not found: {server_conn}")
    
    if not db_conn_serv.exists():
        raise FileNotFoundError(f"Server database connection file not found: {db_conn_serv}")
    
    if db_conn_pub and not db_conn_pub.exists():
        raise FileNotFoundError(f"Publisher database connection file not found: {db_conn_pub}")
    
    logger.info(
        "Registering database connection '%s' using server_conn='%s', db_conn_serv='%s'%s",
        connection_name,
        server_conn,
        db_conn_serv,
        f", db_conn_pub='{db_conn_pub}'" if db_conn_pub else "",
    )
    
    # AddDataStoreItem signature: (server_connection_file, datastore_type, connection_name, server_path, {client_path})
    if db_conn_pub:
        # If publisher connection is provided, use it as client_path
        arcpy.AddDataStoreItem(
            str(server_conn),
            "DATABASE",
            connection_name,
            str(db_conn_serv),
            str(db_conn_pub)
        )
    else:
        # If no publisher connection, only provide server_path
        arcpy.AddDataStoreItem(
            str(server_conn),
            "DATABASE",
            connection_name,
            str(db_conn_serv)
        )
    
    logger.info("Successfully registered database connection '%s'", connection_name)


def _validate_data_stores(
    server_conn: Path,
    connection_names: list[str],
    logger: logging.Logger,
) -> dict[str, str]:
    """Validate registered data stores on an ArcGIS Server.
    
    Args:
        server_conn: Path to ArcGIS Server connection file (.ags)
        connection_names: List of connection names to validate (if empty, validates all)
        logger: Logger instance for output
    
    Returns:
        Dictionary mapping connection names to their validation status ('valid' or 'invalid')
    """
    if not server_conn.exists():
        logger.warning("Server connection file not found for validation: %s", server_conn)
        return {}
    
    logger.info("Validating data stores on server: %s", server_conn)
    
    validation_results = {}
    
    try:
        # List all DATABASE data stores
        datastore_items = arcpy.ListDataStoreItems(str(server_conn), "DATABASE")
        
        if not datastore_items:
            logger.info("No DATABASE data stores found on server: %s", server_conn)
            return validation_results
        
        # Filter to only validate specified connection names, or validate all if list is empty
        items_to_validate = datastore_items
        if connection_names:
            items_to_validate = [item for item in datastore_items if item[0] in connection_names]
            if len(items_to_validate) < len(connection_names):
                missing = set(connection_names) - {item[0] for item in items_to_validate}
                logger.warning("Some connection names not found on server: %s", missing)
        
        # Validate each data store
        for item in items_to_validate:
            connection_name = item[0]
            try:
                validity = arcpy.ValidateDataStoreItem(str(server_conn), "DATABASE", connection_name)
                validation_results[connection_name] = validity
                
                if validity.lower() == "valid":
                    logger.info("Data store '%s' is VALID", connection_name)
                else:
                    logger.warning("Data store '%s' is INVALID", connection_name)
            except Exception as e:
                logger.error("Error validating data store '%s': %s", connection_name, str(e))
                validation_results[connection_name] = "error"
        
        # Log summary
        valid_count = sum(1 for v in validation_results.values() if v.lower() == "valid")
        invalid_count = len(validation_results) - valid_count
        
        logger.info(
            "Validation summary for server '%s': %d valid, %d invalid out of %d total data stores",
            server_conn,
            valid_count,
            invalid_count,
            len(validation_results),
        )
        
    except Exception as e:
        logger.error("Error listing/validating data stores on server '%s': %s", server_conn, str(e))
    
    return validation_results


def _load_config(config_path: Path) -> configparser.ConfigParser:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file `{config_path}` does not exist.")

    config = configparser.ConfigParser()
    if not config.read(config_path):
        raise ValueError(f"Unable to read configuration from `{config_path}`.")

    return config


def main(config_path: Optional[Path] = None) -> None:
    config_path = config_path or DEFAULT_CONFIG_PATH
    config = _load_config(config_path)
    base_dir = config_path.parent

    log_dir = _resolve_path(config["DEFAULT"].get("log_directory"), base_dir) if config["DEFAULT"].get("log_directory") else None
    logger = _configure_logging(log_dir)
    logger.info("Starting database registration using configuration `%s`", config_path)

    sections = config.sections()
    if not sections:
        logger.warning("No database sections found in the configuration. Nothing to process.")
        return

    # Track registered connections for validation
    registered_connections: dict[Path, list[str]] = {}  # server_conn -> list of connection_names

    for section in sections:
        db_config = config[section]

        # Required: server connection file
        server_conn_raw = db_config.get("server_conn")
        if not server_conn_raw:
            raise ValueError(f"`server_conn` is required for section `{section}`.")
        server_conn = _resolve_path(server_conn_raw, base_dir)
        if not server_conn:
            raise ValueError(f"`server_conn` cannot be empty for section `{section}`.")

        # Required: server database connection file
        db_conn_serv_raw = db_config.get("db_conn_serv")
        if not db_conn_serv_raw:
            raise ValueError(f"`db_conn_serv` is required for section `{section}`.")
        db_conn_serv = _resolve_path(db_conn_serv_raw, base_dir)
        if not db_conn_serv:
            raise ValueError(f"`db_conn_serv` cannot be empty for section `{section}`.")

        # Optional: publisher database connection file
        db_conn_pub_raw = db_config.get("db_conn_pub")
        db_conn_pub = _resolve_path(db_conn_pub_raw, base_dir) if db_conn_pub_raw else None

        # Connection name (optional, defaults to section name)
        connection_name = db_config.get("connection_name", section)

        logger.info("Processing section `%s`", section)

        _register_database(
            server_conn=server_conn,
            db_conn_serv=db_conn_serv,
            db_conn_pub=db_conn_pub,
            connection_name=connection_name,
            logger=logger,
        )

        # Track this connection for validation
        if server_conn not in registered_connections:
            registered_connections[server_conn] = []
        registered_connections[server_conn].append(connection_name)

    logger.info("Database registration process completed.")

    # Validate all registered data stores
    logger.info("=" * 60)
    logger.info("Starting validation of registered data stores...")
    logger.info("=" * 60)
    
    all_validation_results: dict[Path, dict[str, str]] = {}
    
    for server_conn, connection_names in registered_connections.items():
        validation_results = _validate_data_stores(
            server_conn=server_conn,
            connection_names=connection_names,
            logger=logger,
        )
        all_validation_results[server_conn] = validation_results
    
    # Summary of validation
    logger.info("=" * 60)
    logger.info("Validation Summary:")
    logger.info("=" * 60)
    
    total_valid = 0
    total_invalid = 0
    
    for server_conn, results in all_validation_results.items():
        valid_count = sum(1 for v in results.values() if v.lower() == "valid")
        invalid_count = len(results) - valid_count
        total_valid += valid_count
        total_invalid += invalid_count
        
        logger.info(
            "Server '%s': %d valid, %d invalid",
            server_conn,
            valid_count,
            invalid_count,
        )
    
    logger.info("=" * 60)
    logger.info("Overall: %d valid, %d invalid data stores", total_valid, total_invalid)
    logger.info("=" * 60)
    
    if total_invalid > 0:
        logger.warning("Some data stores failed validation. Please review the logs above.")


if __name__ == "__main__":
    user_supplied_config = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    main(user_supplied_config)
