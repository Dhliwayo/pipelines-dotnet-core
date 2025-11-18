# ArcGIS Server Database Registration Utility

This utility registers SQL Server databases with ArcGIS Server using ArcPy. Database credentials and connection details are stored in a configuration file.

## Overview

The script `register_arcgis_server_database.py` reads database and ArcGIS Server connection information from a configuration file (`config/config.ini`) and registers each specified SQL Server database with ArcGIS Server.

## Requirements

- ArcGIS Desktop or ArcGIS Pro with ArcPy installed
- Access to ArcGIS Server with administrative privileges
- SQL Server database access credentials
- 64-bit SQL Server client installed on ArcGIS Server machines (required for ArcGIS Server to communicate with SQL Server databases)

## Configuration

Edit `config/config.ini` to specify:

1. **DEFAULT section**: ArcGIS Server connection details that apply to all databases
   - `target_server_url`: Target ArcGIS Server admin URL where databases will be registered (e.g., `https://myserver:6443/arcgis/admin`)
   - `target_server_username`: Target ArcGIS Server administrator username
   - `target_server_password`: Target ArcGIS Server administrator password
   - `publisher_server_url`: (Optional) Publisher ArcGIS Server URL (where services are published from, if different from target)
   - `publisher_server_username`: (Optional) Publisher ArcGIS Server username
   - `publisher_server_password`: (Optional) Publisher ArcGIS Server password
   - `log_directory`: (Optional) Directory for log files
   
   **Note**: For backward compatibility, `server_url`, `server_username`, and `server_password` can be used instead of `target_server_*` if target values are not specified.

2. **Database sections**: Each section represents a database to register
   - `database_server`: SQL Server instance name (e.g., `myserver` or `myserver\SQLEXPRESS`)
   - `database_name`: Database name to register
   - `database_username`: SQL Server database username
   - `database_password`: SQL Server database password
   - `connection_name`: (Optional) Name for the registered connection (defaults to section name)
   - `target_server_url`, `target_server_username`, `target_server_password`: (Optional) Override default target server for this database
   - `publisher_server_url`, `publisher_server_username`, `publisher_server_password`: (Optional) Override default publisher server for this database

### Example Configuration

#### Simple Configuration (Same Server for Publishing and Registration)

```ini
[DEFAULT]
target_server_url = https://myserver:6443/arcgis/admin
target_server_username = admin
target_server_password = password
log_directory = D:\Logs

[DATABASE_1]
database_server = myserver\SQLEXPRESS
database_name = MyGeodatabase
database_username = dbuser
database_password = dbpassword
connection_name = ProductionDatabase
```

#### Configuration with Separate Publisher and Target Servers

```ini
[DEFAULT]
# Target server where databases are registered
target_server_url = https://target-server:6443/arcgis/admin
target_server_username = target_admin
target_server_password = target_password

# Publisher server where services are published from
publisher_server_url = https://publisher-server:6443/arcgis/admin
publisher_server_username = publisher_admin
publisher_server_password = publisher_password

log_directory = D:\Logs

[DATABASE_1]
database_server = myserver\SQLEXPRESS
database_name = MyGeodatabase
database_username = dbuser
database_password = dbpassword
connection_name = ProductionDatabase
```

## Usage

### Basic Usage

Run the script with the default configuration file:

```bash
python register_arcgis_server_database.py
```

### Custom Configuration File

Specify a custom configuration file path:

```bash
python register_arcgis_server_database.py "C:\Path\To\custom_config.ini"
```

## How It Works

1. **Reads Configuration**: Loads database and ArcGIS Server credentials from the config file
2. **Creates Connection Files**: 
   - Creates a temporary database connection file (.sde) for each SQL Server database
   - Creates a temporary target ArcGIS Server connection file (.ags) for database registration
   - Optionally creates a publisher ArcGIS Server connection file (.ags) if publisher server is configured
3. **Registers Databases**: Uses `arcpy.AddDataStoreItem()` to register each database with the **target** ArcGIS Server
4. **Cleans Up**: Removes temporary connection files after registration

**Important**: Databases are always registered on the **target server**, regardless of publisher server configuration. The publisher server connection is created for reference/validation purposes when services are published from a different server than where databases are registered.

## Logging

The script logs all operations to:
- Console (stdout)
- Log file (if `log_directory` is specified in config)

Log files are named with timestamps: `register_arcgis_server_database_YYYYMMDD_HHMMSS.log`

## Error Handling

The script will:
- Validate that all required configuration values are present
- Verify that connection files are created successfully
- Log errors and raise exceptions if registration fails
- Clean up temporary files even if errors occur

## Security Notes

- Store the configuration file securely and restrict access to authorized users
- Consider using environment variables or secure credential storage for production environments
- The script creates temporary connection files that are automatically cleaned up
- Passwords are stored in connection files temporarily during registration

## Troubleshooting

### Common Issues

1. **"Database connection file was not created"**
   - Verify SQL Server credentials are correct
   - Ensure SQL Server is accessible from the machine running the script
   - Check that the database name exists

2. **"Target ArcGIS Server connection file was not created"**
   - Verify target ArcGIS Server URL is correct
   - Ensure target ArcGIS Server administrator credentials are valid
   - Check network connectivity to target ArcGIS Server
   
3. **"Publisher ArcGIS Server connection file was not created"** (warning only)
   - This is a warning and does not prevent registration
   - Verify publisher ArcGIS Server URL is correct if publisher server is required
   - Ensure publisher ArcGIS Server administrator credentials are valid

4. **Registration fails**
   - Ensure the ArcGIS Server account has permissions to access the SQL Server database
   - Verify that the 64-bit SQL Server client is installed on ArcGIS Server machines
   - Check ArcGIS Server logs for detailed error messages

## Related Documentation

- [ArcGIS Server: Register SQL Server with ArcGIS Server](https://enterprise.arcgis.com/en/server/latest/manage-data/windows/register-sql-server-with-arcgis-server.htm)
- [ArcPy: AddDataStoreItem](https://pro.arcgis.com/en/pro-app/latest/arcpy/functions/adddatastoreitem.htm)

