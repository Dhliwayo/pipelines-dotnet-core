# Unified Python Execution System

**KISS Principle: Keep It Simple, Stupid!**

**ONE PowerShell script** that replaces all your individual PowerShell scripts (`update_feature_class.ps1`, `copy_pnp_configs.ps1`, etc.) and can execute any Python module.

## 🎯 **What This Replaces**

**Before**: Multiple PowerShell scripts doing the same thing
- `update_feature_class.ps1`
- `copy_pnp_configs.ps1` 
- `import_rasters.ps1`
- `update_country_peril.ps1`
- etc.

**After**: **ONE PowerShell script** that handles everything
- `execute_python_module.ps1` - The complete solution

## 🚀 **How to Use**

### Option 1: Simple Module Names (Recommended)

```powershell
# Update geodatabase feature classes
.\execute_python_module.ps1 -ModuleName "update_feature_class"

# Import rasters with verbose output
.\execute_python_module.ps1 -ModuleName "import_rasters" -Verbose

# Copy geodatabases with custom timeout
.\execute_python_module.ps1 -ModuleName "copy_geodatabases" -CustomTimeout 7200

# Update country perils with arguments
.\execute_python_module.ps1 -ModuleName "update_country_peril" -Arguments @("--force", "--validate")
```

### Option 2: Direct Module Paths

```powershell
# Execute any Python module directly
.\execute_python_module.ps1 -ModulePath "update_gdb_feature_classes.update_feature_class"

# With custom parameters
.\execute_python_module.ps1 -ModulePath "import_rasters.import_rasters" -WorkingDirectory "D:\ArcGIS" -TimeoutSeconds 3600
```

## 📋 **Available Modules**

| Module Name | Full Path | Description |
|-------------|-----------|-------------|
| `update_feature_class` | `update_gdb_feature_classes.update_feature_class` | Update geodatabase feature classes |
| `import_rasters` | `import_rasters.import_rasters` | Import raster files |
| `copy_geodatabases` | `copy_geodatabases.copy_geodatabases` | Copy geodatabases |
| `update_country_peril` | `update_country_config.update_country_peril` | Update country perils |
| `update_map_data_source` | `update_maps_data_sources.update_map_data_source` | Update map sources |
| `add_domains` | `domains_add.add_domains` | Add domains |
| `delete_domains` | `domains_remove.delete_domain_entries` | Remove domains |
| `publish_services` | `publish_arcgis_services.update_arcgis_server_services` | Publish services |
| `register_datasets` | `register_datasets.register_data` | Register datasets |

## 🔧 **Pipeline Integration**

### Azure DevOps Pipeline Task

```yaml
- task: PowerShellOnTargetMachines@3
  displayName: 'Execute Python Module'
  inputs:
    Machines: $(server_service_connections)
    UserName: $(pnp_service_account_name)
    UserPassword: $(pnp_service_account_password)
    ScriptType: 'FilePath'
    ScriptPath: $(scriptPath)\execute_python_module.ps1
    ScriptArguments: '-ModuleName "update_feature_class"'
    WorkingDirectory: $(workingDirectory)
    CommunicationProtocol: 'Http'
    AuthenticationMechanism: 'Default'
```

### Pipeline Variables

```yaml
variables:
  scriptPath: '$(Build.SourcesDirectory)\utilities'
  workingDirectory: '$(Build.SourcesDirectory)\arcgis_services\deploy\scripts'
```

## 📁 **File Structure**

```
utilities/
├── execute_python_module.ps1      # THE ONE SCRIPT THAT DOES EVERYTHING
└── README_unified_python_execution.md
```

## 🎨 **Features**

### 1. **Smart Logging**
- Auto-generates log file names based on module
- Real-time output capture
- Structured execution summaries

### 2. **Error Handling**
- Proper exit codes for pipelines
- Detailed error information
- Process cleanup and timeout handling

### 3. **Flexibility**
- Custom working directories
- Configurable timeouts
- Additional arguments support

### 4. **Pipeline Integration**
- Proper exit codes
- Structured output
- Error propagation

## 🔄 **Migration Guide**

### Step 1: Replace Individual Scripts

**Before** (in your pipeline):
```yaml
ScriptPath: $(scriptPath)\update_feature_class.ps1
```

**After**:
```yaml
ScriptPath: $(scriptPath)\execute_python_module.ps1
ScriptArguments: '-ModuleName "update_feature_class"'
```

### Step 2: Update Pipeline Variables

```yaml
variables:
  scriptPath: '$(Build.SourcesDirectory)\utilities'  # Point to utilities folder
```

### Step 3: Test and Deploy

1. Test locally first
2. Update pipeline configurations
3. Deploy to staging
4. Deploy to production

## 📝 **Examples for Different Scenarios**

### 1. **Geodatabase Updates**
```yaml
- task: PowerShellOnTargetMachines@3
  displayName: 'Update Feature Classes'
  inputs:
    ScriptPath: $(scriptPath)\execute_python_module.ps1
    ScriptArguments: '-ModuleName "update_feature_class"'
```

### 2. **Raster Import**
```yaml
- task: PowerShellOnTargetMachines@3
  displayName: 'Import Rasters'
  inputs:
    ScriptPath: $(scriptPath)\execute_python_module.ps1
    ScriptArguments: '-ModuleName "import_rasters" -Verbose'
```

### 3. **Service Publishing**
```yaml
- task: PowerShellOnTargetMachines@3
  displayName: 'Publish Services'
  inputs:
    ScriptPath: $(scriptPath)\execute_python_module.ps1
    ScriptArguments: '-ModuleName "publish_services" -CustomTimeout 7200'
```

## 🚨 **Troubleshooting**

### Common Issues

1. **Module not found**: Check the module name in the ValidateSet
2. **Path issues**: Ensure utilities folder is accessible
3. **Python not found**: Verify Python is in PATH on target machine
4. **Timeout issues**: Increase timeout for long-running operations

### Debug Mode

```powershell
# Enable verbose output
.\execute_python_module.ps1 -ModuleName "update_feature_class" -Verbose

# Check available modules
Get-Help .\execute_python_module.ps1 -Parameter ModuleName
```

## ✅ **Benefits**

1. **ONE script to maintain** - Update one file, fix all issues
2. **Consistent behavior** - Same error handling and logging everywhere
3. **Easy to use** - Simple, intuitive interface
4. **Pipeline friendly** - Proper integration with Azure DevOps
5. **Flexible** - Configurable for different use cases
6. **Maintainable** - Clean, well-documented code
7. **KISS compliant** - No unnecessary complexity or external files
8. **Single source of truth** - Everything in one place

## 🔮 **Future Enhancements**

- Add more Python modules to the script
- Support for custom module paths
- Performance monitoring and metrics

## 📞 **Support**

For questions or issues:
1. Check the troubleshooting section
2. Review the log files
3. Test with verbose output
4. Check module names in the ValidateSet

This unified system gives you the power and flexibility to execute any Python module with **ONE PowerShell script**. **KISS principle applied** - no unnecessary complexity, just simple, effective execution in a single file!
