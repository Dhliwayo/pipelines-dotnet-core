# Validate copied geodatabases by comparing their hashes with expected values from config

Write-Output "Starting geodatabase hash validation..."

try {
    # Read config file to get source/destination paths and expected hashes
    $configPath = Join-Path $PSScriptRoot "config\config.ini"
    if (!(Test-Path $configPath)) {
        throw "Config file not found: $configPath"
    }
    
    $config = Get-Content $configPath -Raw | ConvertFrom-IniString
    
    Function Test-Fgdb-Hash {
        param (
            $FgdbPath,
            $ExpectedHash
        )
        
        # Calculate actual hash
        $HashString = (Get-ChildItem $FgdbPath -Recurse | Get-FileHash -Algorithm MD5).Hash | Out-String
        $ActualHash = (Get-FileHash -InputStream ([IO.MemoryStream]::new([char[]]$HashString))).Hash
        
        # Compare hashes
        if ($ActualHash -eq $ExpectedHash) {
            Write-Output "✓ Hash match for: $FgdbPath"
            return $true
        } else {
            Write-Error "✗ Hash mismatch for: $FgdbPath"
            Write-Error "Expected: $ExpectedHash"
            Write-Error "Actual:   $ActualHash"
            return $false
        }
    }
    
    $allValid = $true
    
    foreach ($section in $config.GetEnumerator()) {
        if ($section.Key -eq 'DEFAULT') { continue }
        
        $destinationPath = $section.Value.destination_path
        $expectedHash = $section.Value.expected_hash
        
        Write-Output "Validating: $destinationPath"
        
        if (!(Test-Path $destinationPath)) {
            Write-Error "Destination path not found: $destinationPath"
            $allValid = $false
            continue
        }
        
        if (!(Test-Fgdb-Hash -FgdbPath $destinationPath -ExpectedHash $expectedHash)) {
            $allValid = $false
        }
    }
    
    # Exit with appropriate code
    if ($allValid) {
        Write-Output "All geodatabases validated successfully!"
        exit 0
    } else {
        Write-Error "Hash validation failed for one or more geodatabases!"
        exit 1
    }
    
} catch {
    Write-Error "Error during geodatabase validation: $_"
    exit 1
}