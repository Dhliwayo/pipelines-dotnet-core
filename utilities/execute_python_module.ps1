# Usage examplses: 
# .\execute_python_module.ps1 -ModulePath "update_gdb_feature_classes.update_feature_class" -WorkingDirectory "D:\scripts\data_preparation"
# .\execute_python_module.ps1 -ModulePath "copy_geodatabases.copy_geodatabases" -WorkingDirectory "D:\scripts\data_release"

#Yaml example:
# ScriptArguments: '-ModulePath "update_gdb_feature_classes.update_feature_class" -WorkingDirectory "$(scriptPath)\arcgis_services\deploy\scripts\data_preparation"'

param(
    [Parameter(Mandatory=$true)]
    [string]$ModulePath,
    
    [Parameter(Mandatory=$true)]
    [string]$WorkingDirectory,
    
    [Parameter(Mandatory=$false)]
    [string]$DBUsername,
    
    [Parameter(Mandatory=$false)]
    [SecureString]$DBPassword,
    
    [Parameter(Mandatory=$false)]
    [string]$DBServer,
    
    [Parameter(Mandatory=$false)]
    [string]$DBName
)

# Set working directory
if (!(Test-Path $WorkingDirectory)) {
    Write-Error "Working directory does not exist: $WorkingDirectory"
    exit 1
}
Set-Location -Path $WorkingDirectory
Write-Output "Working directory: $WorkingDirectory"

# Build additional arguments for Python module
$additionalArgs = @()

if ($DBUsername) { 
    $additionalArgs += "--db-username"
    $additionalArgs += $DBUsername
}
if ($DBPassword) { 
    $additionalArgs += "--db-password"
    # Convert SecureString to plain text for Python argument
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($DBPassword)
    $plainPassword = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
    $additionalArgs += $plainPassword
    # Clear the plain text password from memory
    [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($BSTR)
}
if ($DBServer) { 
    $additionalArgs += "--db-server"
    $additionalArgs += $DBServer
}
if ($DBName) { 
    $additionalArgs += "--db-name"
    $additionalArgs += $DBName
}

Write-Output "Executing Python module: $ModulePath"
if ($additionalArgs.Count -gt 0) {
    Write-Output "With additional arguments: $($additionalArgs -join ' ')"
}

# Execute Python module with additional arguments
if ($additionalArgs.Count -gt 0) {
    python -m $ModulePath @additionalArgs
} else {
    python -m $ModulePath
}

# Check exit code
if ($LASTEXITCODE -ne 0) {
    Write-Error "Python module failed with exit code $LASTEXITCODE"
    exit $LASTEXITCODE
}

Write-Output "Python module completed successfully"
