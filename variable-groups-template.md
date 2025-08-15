# Azure DevOps Variable Groups Configuration

This document describes the variable groups that need to be created in Azure DevOps for the SQL deployment pipeline to work.

## Required Variable Groups

### 1. SQL-Deployment-Staging
**Group Name:** `SQL-Deployment-staging`

| Variable Name | Description | Example Value | Is Secret |
|---------------|-------------|---------------|-----------|
| `targetMachine` | Target machine hostname or IP | `staging-server.company.com` | No |
| `winrmUsername` | WinRM username | `deploy-user` | No |
| `winrmPassword` | WinRM password | `********` | **Yes** |
| `sqlServer` | SQL Server instance | `staging-sql.company.com` | No |
| `databaseName` | Target database name | `MyApp_Staging` | No |
| `sqlUsername` | SQL Server username | `deploy-user` | No |
| `sqlPassword` | SQL Server password | `********` | **Yes** |
| `backupLocation` | Database backup location | `D:\DatabaseBackups` | No |

### 2. SQL-Deployment-Production
**Group Name:** `SQL-Deployment-production`

| Variable Name | Description | Example Value | Is Secret |
|---------------|-------------|---------------|-----------|
| `targetMachine` | Target machine hostname or IP | `prod-server.company.com` | No |
| `winrmUsername` | WinRM username | `deploy-user` | No |
| `winrmPassword` | WinRM password | `********` | **Yes** |
| `sqlServer` | SQL Server instance | `prod-sql.company.com` | No |
| `databaseName` | Target database name | `MyApp_Production` | No |
| `sqlUsername` | SQL Server username | `deploy-user` | No |
| `sqlPassword` | SQL Server password | `********` | **Yes** |
| `backupLocation` | Database backup location | `E:\DatabaseBackups` | No |

## How to Create Variable Groups

1. **Navigate to Azure DevOps:**
   - Go to your Azure DevOps organization
   - Select your project
   - Go to **Library** → **Variable groups**

2. **Create New Variable Group:**
   - Click **+ Variable group**
   - Name: `SQL-Deployment-staging` or `SQL-Deployment-production`
   - Description: `Variables for SQL deployment to [environment]`
   - Variable group scope: Select appropriate project

3. **Add Variables:**
   - Click **+ Add** for each variable
   - Set the variable name and value
   - Check **Keep this value secret** for passwords
   - Click **Save**

4. **Link to Pipeline:**
   - The pipeline automatically references these variable groups using the naming convention
   - No additional linking required

## Security Considerations

- **Mark passwords as secrets** to prevent them from being exposed in logs
- **Use service accounts** with minimal required permissions
- **Rotate credentials regularly** according to your security policy
- **Limit access** to variable groups to only authorized team members

## WinRM Configuration Requirements

Ensure the target machines have WinRM properly configured:

1. **Enable WinRM service**
2. **Configure HTTPS listener** (port 5986)
3. **Set appropriate firewall rules**
4. **Configure authentication and authorization**
5. **Install required certificates** for HTTPS

## SQL Server Requirements

- **SQL Server Management Objects (SMO)** must be available
- **SqlServer PowerShell module** should be installed
- **User account** must have appropriate permissions for:
  - Database backup
  - Script execution
  - Reading system tables
