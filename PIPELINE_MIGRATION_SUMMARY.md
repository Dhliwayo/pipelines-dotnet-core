# Pipeline Migration Summary - Unified Python Execution

## Overview
All Azure DevOps pipelines have been updated to use the new unified `execute_python_module.ps1` script instead of individual PowerShell scripts for each Python module.

## What Changed

### 1. **Rsa.PerilsProximity.Data.Release.Prep.yml**
- **Before**: Used `update_feature_class.ps1`
- **After**: Uses `utilities/execute_python_module.ps1`
- **ScriptArguments**: `-ModulePath "update_gdb_feature_classes.update_feature_class" -WorkingDirectory "$(updateGdbFeatureClassesWorkingDir)"`
- **Added**: CopyFiles task for utilities folder

### 2. **Rsa.PerilsProximity.Data.Release.yml**
- **Before**: Used `add_domains.ps1` and `copy_geodatabases.ps1`
- **After**: Uses `utilities/execute_python_module.ps1` for both
- **ScriptArguments for AddDomains**: `-ModulePath "domains_add.add_domains" -WorkingDirectory "$(manageDomainsWorkingDir)"`
- **ScriptArguments for CopyGeoDatabases**: `-ModulePath "copy_geodatabases.copy_geodatabases" -WorkingDirectory "$(CopyGeoDatabasesWorkingDir)"`
- **Added**: CopyFiles task for utilities folder

### 3. **azure-pipelines.yml**
- **Before**: Used `arcgis_services/deploy/scripts/4_deploy_domains/add_domains.ps1`
- **After**: Uses `utilities/execute_python_module.ps1`
- **ScriptArguments**: `-ModulePath "domains_add.add_domains" -WorkingDirectory "$(working_directory)\$(build_artifact_name)\arcgis_services\deploy\scripts\4_deploy_domains"`
- **Added**: `utilities/execute_python_module.ps1` to CopyFiles task

## Benefits of Migration

### ✅ **Unified Approach**
- **One script** handles all Python module execution
- **Consistent behavior** across all pipelines
- **Easier maintenance** - update one script instead of many

### ✅ **Better Error Handling**
- **Proper exit codes** for pipeline integration
- **Standardized logging** and output
- **Consistent failure reporting**

### ✅ **Simplified Pipeline Configuration**
- **Same script path** for all stages
- **Parameterized execution** via ScriptArguments
- **Cleaner pipeline definitions**

## Usage Examples

### **Update Feature Classes**
```yaml
ScriptPath: $(pnp_config_working_directory)\$(build_artifact_name)\utilities\execute_python_module.ps1
ScriptArguments: '-ModulePath "update_gdb_feature_classes.update_feature_class" -WorkingDirectory "$(updateGdbFeatureClassesWorkingDir)"'
```

### **Add Domains**
```yaml
ScriptPath: $(pnp_config_working_directory)\$(build_artifact_name)\utilities\execute_python_module.ps1
ScriptArguments: '-ModulePath "domains_add.add_domains" -WorkingDirectory "$(manageDomainsWorkingDir)"'
```

### **Copy Geodatabases**
```yaml
ScriptPath: $(pnp_config_working_directory)\$(build_artifact_name)\utilities\execute_python_module.ps1
ScriptArguments: '-ModulePath "copy_geodatabases.copy_geodatabases" -WorkingDirectory "$(CopyGeoDatabasesWorkingDir)"'
```

## Required Changes

### **Build Artifacts**
All pipelines now include the `utilities/` folder to ensure `execute_python_module.ps1` is available on target machines.

### **Script Arguments**
Each pipeline stage now uses `ScriptArguments` to pass:
- `ModulePath`: The Python module to execute
- `WorkingDirectory`: The directory where the Python script and config files are located

## Migration Complete ✅

All pipelines have been successfully migrated to use the unified approach. The old individual PowerShell scripts can now be safely removed from the repository.
