Write-Output "Starting geodatabase copy process..."

try {
    # Read config file to get source and destination paths
    $configPath = Join-Path $PSScriptRoot "config\config.ini"
    if (!(Test-Path $configPath)) {
        throw "Config file not found: $configPath"
    }
    
    $config = Get-Content $configPath -Raw | ConvertFrom-IniString
    
    # Process each section in config
    foreach ($section in $config.GetEnumerator()) {
        if ($section.Key -eq 'DEFAULT') { continue }
        
        Write-Output "Processing section: $($section.Key)"
        
        $sourcePath = $section.Value.source_path
        $destinationPath = $section.Value.destination_path
        
        Write-Output "Copying from: $sourcePath"
        Write-Output "Copying to: $destinationPath"
        
        # Create destination directory if it doesn't exist
        $destDir = Split-Path $destinationPath -Parent
        if (!(Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            Write-Output "Created destination directory: $destDir"
        }
        
        # Copy the files
        Copy-Item -Path $sourcePath -Destination $destinationPath -Recurse -Force
        
        Write-Output "Copy completed: $sourcePath -> $destinationPath"
    }
    
    Write-Output "All geodatabase copies completed successfully"
    
} catch {
    Write-Error "Error during geodatabase copy: $_"
    exit 1
}