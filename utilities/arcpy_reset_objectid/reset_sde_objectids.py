"""Utility to reset ArcSDE-managed OBJECTID values by truncating and reloading tables.

The script reads configuration from ``config/config.ini`` in the same directory. Each
section describes a table to refresh and can optionally override the defaults for the
ArcSDE connection, scratch workspace, and log directory.
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
    if not raw_path:
        return None

    expanded = os.path.expandvars(raw_path)
    candidate = Path(expanded)
    if not candidate.is_absolute():
        candidate = (base_dir / candidate).resolve()
    return candidate


def _configure_logging(log_directory: Optional[Path]) -> logging.Logger:
    logger = logging.getLogger("reset_sde_objectids")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_directory:
        log_directory.mkdir(parents=True, exist_ok=True)
        log_path = log_directory / f"reset_sde_objectids_{datetime.now():%Y%m%d_%H%M%S}.log"
        file_handler = logging.FileHandler(log_path)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _copy_dataset(source: str, scratch_workspace: str, logger: logging.Logger) -> str:
    description = arcpy.Describe(source)
    base_name = getattr(description, "baseName", Path(source).stem)
    unique_name = arcpy.CreateUniqueName(f"{base_name}_copy", scratch_workspace)

    logger.info("Creating scratch copy of `%s` at `%s`", source, unique_name)

    if hasattr(description, "shapeType"):
        arcpy.management.CopyFeatures(source, unique_name)
    else:
        arcpy.management.CopyRows(source, unique_name)

    return unique_name


def _truncate_and_reload(
    sde_connection: Path,
    target_table: str,
    scratch_workspace: Optional[Path],
    logger: logging.Logger,
) -> None:
    workspace = str(sde_connection)
    arcpy.env.workspace = workspace
    arcpy.env.overwriteOutput = True

    if not arcpy.Exists(target_table):
        raise ValueError(f"Target `{target_table}` not found in `{workspace}`.")

    scratch = scratch_workspace or (Path(arcpy.env.scratchGDB) if arcpy.env.scratchGDB else None)
    if not scratch:
        raise ValueError(
            "Scratch workspace is not defined. Provide `scratch_workspace` in the config or "
            "ensure `arcpy.env.scratchGDB` is available."
        )

    if not arcpy.Exists(str(scratch)):
        raise ValueError(f"Scratch workspace `{scratch}` does not exist or is not accessible.")

    backup_path = None

    try:
        backup_path = _copy_dataset(target_table, str(scratch), logger)

        logger.info("Truncating `%s` using `%s`", target_table, workspace)
        arcpy.management.TruncateTable(target_table)

        logger.info("Appending `%s` back into `%s`", backup_path, target_table)
        arcpy.management.Append(inputs=backup_path, target=target_table, schema_type="NO_TEST")

        logger.info("Reload complete for `%s`. OBJECTID values refreshed by ArcSDE.", target_table)
    finally:
        if backup_path and arcpy.Exists(backup_path):
            logger.info("Removing scratch copy `%s`", backup_path)
            arcpy.management.Delete(backup_path)


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

    default_sde = _resolve_path(config["DEFAULT"].get("sde_connection"), base_dir)
    default_scratch = _resolve_path(config["DEFAULT"].get("scratch_workspace"), base_dir)
    log_dir = _resolve_path(config["DEFAULT"].get("log_directory"), base_dir)

    logger = _configure_logging(log_dir)
    logger.info("Starting OBJECTID reset using configuration `%s`", config_path)

    sections = config.sections()
    if not sections:
        logger.warning("No table sections found in the configuration. Nothing to process.")
        return

    for section in sections:
        table_config = config[section]

        sde_path = _resolve_path(table_config.get("sde_connection"), base_dir) or default_sde
        if not sde_path:
            raise ValueError(
                f"`sde_connection` is not defined for section `{section}` and no default is specified."
            )

        target_table = table_config.get("target_table")
        if not target_table:
            raise ValueError(f"`target_table` is required for section `{section}`.")

        scratch_workspace = _resolve_path(table_config.get("scratch_workspace"), base_dir) or default_scratch

        logger.info("Processing section `%s` targeting table `%s`", section, target_table)

        _truncate_and_reload(sde_path, target_table, scratch_workspace, logger)


if __name__ == "__main__":
    user_supplied_config = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else None
    main(user_supplied_config)

