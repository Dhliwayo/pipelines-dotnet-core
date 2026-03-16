# Azure Pipeline Token Replacement Guide

## How Variables from Library Variable Groups Are Applied

### Step-by-Step Process

1. **Variable Group Loading**
   ```
   Pipeline YAML: - group: PerilsProximity.Configs.${{ parameters.environment }}
   ↓
   Azure DevOps loads variables from: PerilsProximity.Configs.staging
   ↓
   Variables available: DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD, etc.
   ```

2. **XML Transformation**
   ```
   Web.config (source) + Web.PreProd.config (transform) → Transformed Web.config
   ↓
   Tokens like #{DB_SERVER}# are preserved during transformation
   ```

3. **Token Replacement** (NEW STEP ADDED)
   ```
   PowerShell script scans all .config files
   ↓
   Replaces: #{DB_SERVER}# → $(DB_SERVER) → preprod-sql.company.com
   ↓
   Final configuration with actual values
   ```

4. **Deployment**
   ```
   Transformed + Token-replaced files → Target servers
   ```

### Example Flow

#### Input Files:
**Web.config (source):**
```xml
<add name="MyConnection" 
     connectionString="Data Source=xxx;Initial Catalog=ttt;..." />
```

**Web.PreProd.config (transform):**
```xml
<add name="MyConnection" 
     connectionString="Data Source=#{DB_SERVER}#;Initial Catalog=#{DB_NAME}#;User ID=#{DB_USER}#;Password=#{DB_PASSWORD}#" 
     xdt:Transform="SetAttributes" 
     xdt:Locator="Match(name)"/>
```

**Variable Group: PerilsProximity.Configs.preprod**
```
DB_SERVER = preprod-sql.company.com
DB_NAME = PerilsProximity_PreProd  
DB_USER = deploy_user
DB_PASSWORD = secretpassword123
```

#### After XML Transformation:
```xml
<add name="MyConnection" 
     connectionString="Data Source=#{DB_SERVER}#;Initial Catalog=#{DB_NAME}#;User ID=#{DB_USER}#;Password=#{DB_PASSWORD}#" />
```

#### After Token Replacement:
```xml
<add name="MyConnection" 
     connectionString="Data Source=preprod-sql.company.com;Initial Catalog=PerilsProximity_PreProd;User ID=deploy_user;Password=secretpassword123" />
```

## Key Points

### 1. Variable Group Naming Convention
- **MUST** follow exact pattern: `PerilsProximity.Configs.[environment]`
- Environment values: `staging`, `fint`, `preprod`, `production`

### 2. Token Syntax
- Use `#{VARIABLE_NAME}#` format in transform files
- Pipeline replaces with actual values from variable groups

### 3. Security
- Mark passwords as **secrets** in variable groups
- Values are encrypted and not visible in logs

### 4. Order of Operations
1. Load variable groups
2. Apply XML transforms  
3. Replace tokens (NEW)
4. Deploy to servers

### 5. Supported File Types
Token replacement works on:
- `*.config` files
- `*.xml` files  
- `*.ini` files

## Troubleshooting

### Variables Not Loading
- Check variable group name matches exactly
- Verify pipeline has access to the variable group
- Ensure variables are not marked as secrets if accessed in logs

### Tokens Not Replaced
- Verify token syntax: `#{VARIABLE_NAME}#`
- Check the PowerShell script runs after XML transforms
- Ensure variable exists in the variable group

### Permission Issues
- Grant pipeline service connection access to variable groups
- Check user has View/Use permissions on variable groups

## Files Created/Modified

1. **azure-pipelines.yml** - Added token replacement step
2. **variable-groups-perilsproximity-template.md** - Complete variable group setup guide
3. **Web.PreProd.config** - Example transform with tokens (already correct)
4. **Web.Production.config** - Updated to use tokens
5. **utilities/test_transform.ps1** - Local testing tool
6. **utilities/test_batchmanager_transform.ps1** - Quick test script
7. **utilities/README_transform_testing.md** - Testing documentation

## Next Steps

1. **Create variable groups** in Azure DevOps using the template
2. **Test locally** using the PowerShell scripts
3. **Run pipeline** to verify token replacement works
4. **Deploy** and verify final configuration

The pipeline will now automatically replace tokens with values from your variable groups!
