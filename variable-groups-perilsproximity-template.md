# Azure DevOps Variable Groups for PerilsProximity Pipeline

This document describes the variable groups that need to be created in Azure DevOps for the PerilsProximity configuration deployment pipeline.

## Variable Group Naming Convention

Variable groups must follow this naming pattern:
- `PerilsProximity.Configs.staging`
- `PerilsProximity.Configs.fint`  
- `PerilsProximity.Configs.preprod`
- `PerilsProximity.Configs.production`

## Required Variable Groups

### 1. PerilsProximity.Configs.Staging
**Group Name:** `PerilsProximity.Configs.staging`

| Variable Name | Description | Example Value | Is Secret | Required |
|---------------|-------------|---------------|-----------|----------|
| `DB_SERVER` | Database server hostname/IP | `staging-sql.company.com` | No | Yes |
| `DB_NAME` | Database name | `PerilsProximity_Staging` | No | Yes |
| `DB_USER` | Database username | `deploy_user` | No | Yes |
| `DB_PASSWORD` | Database password | `********` | **Yes** | Yes |
| `API_ENDPOINT` | API base URL | `https://staging-api.company.com` | No | No |
| `Environment` | Environment identifier | `Staging` | No | No |
| `server_service_connections` | Comma-separated server list | `staging-server1,staging-server2` | No | Yes |
| `pnp_service_account_name` | Service account username | `domain\svc_pnp` | No | Yes |
| `pnp_service_account_password` | Service account password | `********` | **Yes** | Yes |
| `working_directory` | Target deployment directory | `C:\PnPConfigsDeployment` | No | Yes |

### 2. PerilsProximity.Configs.PreProd
**Group Name:** `PerilsProximity.Configs.preprod`

| Variable Name | Description | Example Value | Is Secret | Required |
|---------------|-------------|---------------|-----------|----------|
| `DB_SERVER` | Database server hostname/IP | `preprod-sql.company.com` | No | Yes |
| `DB_NAME` | Database name | `PerilsProximity_PreProd` | No | Yes |
| `DB_USER` | Database username | `deploy_user` | No | Yes |
| `DB_PASSWORD` | Database password | `********` | **Yes** | Yes |
| `API_ENDPOINT` | API base URL | `https://preprod-api.company.com` | No | No |
| `Environment` | Environment identifier | `PreProduction` | No | No |
| `server_service_connections` | Comma-separated server list | `preprod-server1` | No | Yes |
| `pnp_service_account_name` | Service account username | `domain\svc_pnp` | No | Yes |
| `pnp_service_account_password` | Service account password | `********` | **Yes** | Yes |
| `working_directory` | Target deployment directory | `C:\PnPConfigsDeployment` | No | Yes |

### 3. PerilsProximity.Configs.Production
**Group Name:** `PerilsProximity.Configs.production`

| Variable Name | Description | Example Value | Is Secret | Required |
|---------------|-------------|---------------|-----------|----------|
| `DB_SERVER` | Database server hostname/IP | `prod-sql.company.com` | No | Yes |
| `DB_NAME` | Database name | `PerilsProximity_Production` | No | Yes |
| `DB_USER` | Database username | `deploy_user` | No | Yes |
| `DB_PASSWORD` | Database password | `********` | **Yes** | Yes |
| `API_ENDPOINT` | API base URL | `https://api.company.com` | No | No |
| `Environment` | Environment identifier | `Production` | No | No |
| `server_service_connections` | Comma-separated server list | `prod-server1,prod-server2` | No | Yes |
| `pnp_service_account_name` | Service account username | `domain\svc_pnp` | No | Yes |
| `pnp_service_account_password` | Service account password | `********` | **Yes** | Yes |
| `working_directory` | Target deployment directory | `C:\PnPConfigsDeployment` | No | Yes |

## How Token Replacement Works

### 1. Transform Files Use Tokens

Your transform files (like `Web.PreProd.config`) should contain tokens:

```xml
<add name="MyConnection" 
     connectionString="Data Source=#{DB_SERVER}#;Initial Catalog=#{DB_NAME}#;User ID=#{DB_USER}#;Password=#{DB_PASSWORD}#" 
     xdt:Transform="SetAttributes" 
     xdt:Locator="Match(name)"/>
```

### 2. Pipeline Replaces Tokens

The pipeline automatically replaces these tokens:
- `#{DB_SERVER}#` → `$(DB_SERVER)` (from variable group)
- `#{DB_NAME}#` → `$(DB_NAME)` (from variable group)
- `#{DB_USER}#` → `$(DB_USER)` (from variable group)
- `#{DB_PASSWORD}#` → `$(DB_PASSWORD)` (from variable group)

### 3. Final Result

After transformation and token replacement, your config becomes:

```xml
<add name="MyConnection" 
     connectionString="Data Source=preprod-sql.company.com;Initial Catalog=PerilsProximity_PreProd;User ID=deploy_user;Password=actualpassword123" 
     xdt:Transform="SetAttributes" 
     xdt:Locator="Match(name)"/>
```

## How to Create Variable Groups

### Step 1: Navigate to Azure DevOps
1. Go to your Azure DevOps organization
2. Select your project
3. Go to **Pipelines** → **Library** → **Variable groups**

### Step 2: Create Variable Group
1. Click **+ Variable group**
2. **Name:** `PerilsProximity.Configs.staging` (or preprod/production)
3. **Description:** `Variables for PerilsProximity config deployment to staging`
4. **Variable group scope:** Select your project
5. Click **Save**

### Step 3: Add Variables
For each variable in the table above:
1. Click **+ Add**
2. **Name:** Enter the variable name (e.g., `DB_SERVER`)
3. **Value:** Enter the variable value
4. **Keep this value secret:** Check this for passwords
5. Click **Save**

### Step 4: Grant Access
1. Click **Security**
2. Add the appropriate users/groups
3. Set **View** and **Use** permissions

## Security Best Practices

### 1. Mark Sensitive Values as Secrets
Always mark these as secrets:
- `DB_PASSWORD`
- `pnp_service_account_password`

### 2. Use Service Accounts
- Create dedicated service accounts for deployment
- Grant minimal required permissions
- Use domain accounts when possible

### 3. Rotate Credentials Regularly
- Set up a schedule to rotate passwords
- Update variable groups when passwords change
- Document the rotation process

### 4. Limit Access
- Only grant access to authorized team members
- Use Azure AD groups when possible
- Review access regularly

## Troubleshooting

### Variable Not Found Error
```
##[error]Variable 'DB_SERVER' not found
```
**Solution:** Ensure the variable group name matches exactly: `PerilsProximity.Configs.[environment]`

### Token Not Replaced
If tokens like `#{DB_SERVER}#` remain in your final config:
1. Check the variable group contains the variable
2. Verify the token replacement step runs after XML transforms
3. Check the regex pattern in the PowerShell script

### Permission Denied
```
##[error]Access denied to variable group
```
**Solution:** Grant the pipeline service connection access to the variable group

## Example Variable Group Setup Script

You can use this PowerShell script to verify your variable groups:

```powershell
# Connect to Azure DevOps
$orgUrl = "https://dev.azure.com/yourorg"
$projectName = "yourproject"
$personalAccessToken = "your-pat"

# Install Azure DevOps module if needed
Install-Module -Name VSTeam -Force

# Connect
Set-VSTeamAccount -Account $orgUrl -PersonalAccessToken $personalAccessToken

# List variable groups
Get-VSTeamVariableGroup -ProjectName $projectName | Where-Object { $_.name -like "PerilsProximity.Configs.*" }
```

## Additional Resources

- [Azure DevOps Variable Groups](https://docs.microsoft.com/en-us/azure/devops/pipelines/library/variable-groups)
- [Secure Variables](https://docs.microsoft.com/en-us/azure/devops/pipelines/process/variables#secret-variables)
- [Pipeline Security](https://docs.microsoft.com/en-us/azure/devops/pipelines/security/)
