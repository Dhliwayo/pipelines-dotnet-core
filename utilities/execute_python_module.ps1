# Usage examplses: 
# .\execute_python_module.ps1 -ModulePath "update_gdb_feature_classes.update_feature_class" -WorkingDirectory "D:\scripts\data_preparation"
# .\execute_python_module.ps1 -ModulePath "copy_geodatabases.copy_geodatabases" -WorkingDirectory "D:\scripts\data_release"

#Yaml example:
# ScriptArguments: '-ModulePath "update_gdb_feature_classes.update_feature_class" -WorkingDirectory "$(scriptPath)\arcgis_services\deploy\scripts\data_preparation"'

param(
    [Parameter(Mandatory=$true)]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$true)]
    [string]$WorkingDirectory
)

# Set working directory
if (!(Test-Path $WorkingDirectory)) {
    Write-Error "Working directory does not exist: $WorkingDirectory"
    exit 1
}
Set-Location -Path $WorkingDirectory
Write-Output "Working directory: $WorkingDirectory"

Write-Output "Executing Python module: $ModulePath"

# Execute Python module
python -m $ModulePath

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python module failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Output "Python module completed successfully"
