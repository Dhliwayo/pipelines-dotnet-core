# Validate copied geodatabases by comparing their hashes with expected values from config

Write-Output "Starting geodatabase hash validation..."

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
    # Read config file to get source/destination paths and expected hashes
    $configPath = Join-Path $PSScriptRoot "config\config.ini"
    if (!(Test-Path $configPath)) {
        throw "Config file not found: $configPath"
    }
    
    $config = Read-IniFile -Path $configPath
    
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
        
        $destinationPath = $section.Value['destination_path']
        $expectedHash = $section.Value['expected_hash']
        
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

D:\PnPGeoRiskDeploymentWorkingDir\Build-drop-staging\arcgis_services\deploy\scripts\data_release\c
At line:1 char:1
+ & 'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe' -NoLogo ...
+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (D:\PnPGeoRiskDe...\data_release\c:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 

opy_geodatabases\validate_file_geodatabase.ps1 : Error during geodatabase validation  Hash 
validation failed for one or more geodatabases!
At C:\Users\GRAUDATA\AppData\Local\Temp\69d03b76-579c-462f-9346-23e2666529f7.ps1:12 char:13


+             . 'D:\PnPGeoRiskDeploymentWorkingDir\Build-drop-staging\a ...


+             ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


    + CategoryInfo          : NotSpecified: (:) [Write-Error], WriteErrorException


    + FullyQualifiedErrorId : Microsoft.PowerShell.Commands.WriteErrorException,validate_file_geo 


   database.ps1
