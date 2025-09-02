Write-Output "Starting geodatabase copy process..."

function Read-IniFile {
    param(
        [Parameter(Mandatory=$true)]
        [string]$Path
    )
    if (!(Test-Path $Path)) {
        throw "INI file not found: $Path"
    }
    $ini = @{}
    $currentSection = $null
    foreach ($rawLine in Get-Content -Path $Path) {
        $line = $rawLine.Trim()
        if ($line -eq '' -or $line.StartsWith(';') -or $line.StartsWith('#')) { continue }
        if ($line.StartsWith('[') -and $line.EndsWith(']')) {
            $sectionName = $line.TrimStart('[').TrimEnd(']')
            if (-not $ini.ContainsKey($sectionName)) { $ini[$sectionName] = @{} }
            $currentSection = $sectionName
            continue
        }
        $eqIndex = $line.IndexOf('=')
        if ($eqIndex -gt 0 -and $currentSection) {
            $key = $line.Substring(0, $eqIndex).Trim()
            $value = $line.Substring($eqIndex + 1).Trim()
            $ini[$currentSection][$key] = $value
        }
    }
    return $ini
}

try {
    # Read config file to get source and destination paths
    $configPath = Join-Path $PSScriptRoot "config\config.ini"
    if (!(Test-Path $configPath)) {
        throw "Config file not found: $configPath"
    }
    
    $config = Read-IniFile -Path $configPath
    
    # Process each section in config
    foreach ($section in $config.GetEnumerator()) {
        if ($section.Key -eq 'DEFAULT') { continue }
        
        Write-Output "Processing section: $($section.Key)"
        
        $shouldUpdate = $true
        if ($section.Value.ContainsKey('update_in_release')) {
            $flag = ($section.Value['update_in_release'] | Out-String).Trim().ToLower()
            if ($flag -in @('false','0','no','off')) { $shouldUpdate = $false }
        }
        if (-not $shouldUpdate) {
            Write-Output "Skipping section '$($section.Key)' because update_in_release is set to false"
            continue
        }
        
        $sourcePath = $section.Value['source_path']
        $destinationPath = $section.Value['destination_path']
        
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