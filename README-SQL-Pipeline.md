# SQL Server Deployment Pipeline

This Azure DevOps pipeline automates the deployment of SQL Server scripts to target environments using WinRM and PowerShell.

## Features

- ✅ **Environment Selection**: Choose between staging and production
- ✅ **WinRM Execution**: Remotely execute scripts on target machines
- ✅ **Database Backup**: Automatic backup before script execution
- ✅ **Variable Library Integration**: Secure credential management
- ✅ **Script Ordering**: Executes scripts in proper sequence
- ✅ **Error Handling**: Comprehensive error handling and rollback
- ✅ **Automatic Rollback**: Database restoration on deployment failure
- ✅ **Deployment Verification**: Post-deployment validation
- ✅ **Audit Trail**: Detailed deployment reports and logs

## Pipeline Structure

```
SQL-Deployment-Pipeline
├── Validate Stage          # Validate environment and parameters
├── Prepare Stage          # Prepare deployment artifacts
├── Deploy Stage          # Execute deployment on target machine
├── Rollback Stage        # Restore database on failure (automatic)
└── PostDeployment Stage  # Generate reports and cleanup
```

## Prerequisites

### 1. Azure DevOps Setup
- Azure DevOps organization and project
- Agent pool with Windows capabilities
- Appropriate permissions to create pipelines and variable groups

### 2. Target Machine Requirements
- Windows Server with WinRM enabled
- PowerShell 5.1 or later
- SQL Server Management Objects (SMO)
- SqlServer PowerShell module
- Appropriate firewall rules (port 5986 for HTTPS)

### 3. SQL Server Requirements
- SQL Server instance accessible from target machine
- User account with backup and script execution permissions
- Sufficient disk space for database backups

## Quick Start

### 1. Create Variable Groups

Create the required variable groups in Azure DevOps:

- `SQL-Deployment-staging`
- `SQL-Deployment-production`

See `variable-groups-template.md` for detailed configuration.

### 2. Add SQL Scripts

Place your SQL scripts in the `sql-scripts/` folder:

```
sql-scripts/
├── 001-schema/
│   └── 001-create-table.sql
├── 002-data/
│   └── 001-insert-data.sql
└── 003-indexes/
    └── 001-create-index.sql
```

### 3. Run the Pipeline

1. Navigate to **Pipelines** in Azure DevOps
2. Select the **SQL-Deployment** pipeline
3. Click **Run pipeline**
4. Select the target environment (staging/production)
5. Configure other parameters as needed
6. Click **Run**

## Pipeline Parameters

| Parameter | Description | Default | Values |
|-----------|-------------|---------|---------|
| `environment` | Target environment | staging | staging, production |
| `skipBackup` | Skip database backup | false | true, false |
| `executeScripts` | Execute SQL scripts | true | true, false |

## Variable Groups

The pipeline automatically references variable groups based on the selected environment:

- **Staging**: `SQL-Deployment-staging`
- **Production**: `SQL-Deployment-production`

### Required Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `targetMachine` | Target machine hostname/IP | Yes |
| `winrmUsername` | WinRM username | Yes |
| `winrmPassword` | WinRM password | Yes |
| `sqlServer` | SQL Server instance | Yes |
| `databaseName` | Target database name | Yes |
| `sqlUsername` | SQL Server username | Yes |
| `sqlPassword` | SQL Server password | Yes |
| `backupLocation` | Database backup location | Yes |

## Script Execution Order

Scripts are executed in the following order:

1. **001-schema/** - Database schema changes
2. **002-data/** - Data insertion/updates
3. **003-indexes/** - Index creation/optimization
4. **004-stored-procedures/** - Stored procedure updates
5. **005-views/** - View updates

Within each folder, scripts are executed alphabetically.

## Security Features

- **Credential Encryption**: Passwords stored as secrets in variable groups
- **WinRM HTTPS**: Secure communication with target machines
- **Least Privilege**: Service accounts with minimal required permissions
- **Audit Logging**: Comprehensive deployment logs and reports

## Rollback Functionality

The pipeline includes an automatic rollback mechanism that activates when any SQL script fails:

### How It Works
1. **Automatic Trigger**: Rollback stage activates only when deployment fails
2. **Backup Tracking**: Uses the specific backup created during deployment
3. **Connection Management**: Safely terminates all database connections
4. **Database Restoration**: Restores the database to its previous state
5. **Verification**: Confirms successful restoration and database health

### Rollback Process
1. **Identify Backup**: Reads backup information from tracking file
2. **Fallback Logic**: If tracking file unavailable, searches for most recent backup
3. **Kill Connections**: Terminates all active database connections
4. **Restore Database**: Executes RESTORE DATABASE command
5. **Verify Status**: Confirms database is ONLINE and accessible
6. **Health Check**: Validates table count and basic functionality

### Benefits
- **Zero Downtime Recovery**: Automatic restoration without manual intervention
- **Data Safety**: Ensures database returns to known good state
- **Audit Trail**: Complete logging of rollback process
- **Fallback Support**: Multiple backup identification methods

## Error Handling

The pipeline includes robust error handling:

- **Validation Stage**: Checks all required variables and connectivity
- **Backup Verification**: Ensures database backup completes successfully
- **Script Execution**: Individual script error handling with detailed logging
- **Automatic Rollback**: Database automatically restored on deployment failure
- **Rollback Verification**: Confirms successful database restoration

## Monitoring and Logging

### Pipeline Logs
- Real-time execution logs in Azure DevOps
- Detailed error messages and stack traces
- Step-by-step execution status
- Rollback execution logs (if triggered)

### Deployment Reports
- Automatic generation of deployment reports
- Database backup verification
- Script execution summary
- Post-deployment validation results
- Rollback status and details (if occurred)

## Troubleshooting

### Common Issues

1. **WinRM Connection Failed**
   - Verify WinRM service is running on target machine
   - Check firewall rules for port 5986
   - Verify credentials in variable groups

2. **SQL Server Connection Failed**
   - Check SQL Server instance name and port
   - Verify user credentials and permissions
   - Ensure SQL Server is accessible from target machine

3. **Script Execution Errors**
   - Review SQL script syntax
   - Check user permissions for specific operations
   - Verify database exists and is accessible

### Debug Mode

Enable verbose logging by setting `$VerbosePreference = 'Continue'` in PowerShell scripts.

## Best Practices

### Script Development
- **Idempotent Scripts**: Scripts should be safe to run multiple times
- **Error Handling**: Include proper TRY-CATCH blocks
- **Transaction Management**: Use transactions for related operations
- **Documentation**: Include clear comments and descriptions

### Pipeline Usage
- **Test in Staging**: Always test in staging before production
- **Review Changes**: Review scripts before deployment
- **Monitor Execution**: Watch pipeline execution for issues
- **Backup Verification**: Verify backups are created successfully
- **Rollback Monitoring**: Monitor rollback execution if deployment fails

### Security
- **Regular Credential Rotation**: Update passwords periodically
- **Access Control**: Limit variable group access to authorized users
- **Audit Logs**: Review deployment logs regularly
- **Network Security**: Use VPN or private networks when possible

## Support

For issues or questions:

1. Check the pipeline logs for detailed error information
2. Review the troubleshooting section above
3. Verify all prerequisites are met
4. Check variable group configuration
5. Ensure target machine WinRM and SQL Server are properly configured

## Contributing

To improve this pipeline:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This pipeline is provided as-is for educational and operational purposes.
