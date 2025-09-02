# Validate copied geodatabases by comparing their hashes with expected values from config

Write-Output "Starting geodatabase hash validation..."

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

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

function Get-CompositeHash {
    param([Parameter(Mandatory=$true)][string]$Path)

    $md5 = [System.Security.Cryptography.MD5]::Create()
    $enc = [System.Text.Encoding]::UTF8

    # Deterministic order
    $files = Get-ChildItem -LiteralPath $Path -Recurse -File -Force -ErrorAction SilentlyContinue | Sort-Object FullName
    foreach ($f in $files) {
        $fileHash = (Get-FileHash -LiteralPath $f.FullName -Algorithm MD5 -ErrorAction SilentlyContinue).Hash
        if (-not [string]::IsNullOrWhiteSpace($fileHash)) {
            $bytes = $enc.GetBytes($fileHash.ToLower())
            [void]$md5.TransformBlock($bytes, 0, $bytes.Length, $null, 0)
        }
    }
    $md5.TransformFinalBlock([byte[]]::new(0), 0, 0)
    return ($md5.Hash | ForEach-Object { $_.ToString('x2') }) -join ''
}

function Test-Fgdb-Hash {
    param(
        [Parameter(Mandatory=$true)] [string]$FgdbPath,
        [Parameter(Mandatory=$true)] [string]$ExpectedHash
    )
    $actual = Get-CompositeHash -Path $FgdbPath
    if ($actual -eq $ExpectedHash) {
        Write-Output "✓ Hash match for: $FgdbPath"
        return $true
    }
    Write-Error "✗ Hash mismatch for: $FgdbPath"
    Write-Error "Expected: $ExpectedHash"
    Write-Error "Actual:   $actual"
    return $false
}

try {
    # Read config file to get source/destination paths and expected hashes
    $configPath = Join-Path $PSScriptRoot "config\config.ini"
    if (!(Test-Path $configPath)) {
        throw "Config file not found: $configPath"
    }
    
    $config = Read-IniFile -Path $configPath
    
    $allValid = $true
    
    foreach ($section in $config.GetEnumerator()) {
        if ($section.Key -eq 'DEFAULT') { continue }

        # Skip if flagged off
        $shouldValidate = $true
        if ($section.Value.ContainsKey('update_in_release')) {
            $flag = ($section.Value['update_in_release'] | Out-String).Trim().ToLower()
            if ($flag -in @('false','0','no','off')) {
                Write-Output "Skipping section '$($section.Key)' (update_in_release=false)"
                continue
            }
        }
        
        # Read and normalize values
        $destinationPath = $section.Value['destination_path']
        $expectedHash = $section.Value['expected_hash']

        $destinationPath = ($destinationPath | Out-String).Trim().Trim('"').Trim("'")
        $expectedHash = ($expectedHash | Out-String).Trim().Trim('"').Trim("'")

        if ([string]::IsNullOrWhiteSpace($destinationPath)) {
            Write-Error "Section '$($section.Key)' missing destination_path. Skipping."
            $allValid = $false
            continue
        }
        if ([string]::IsNullOrWhiteSpace($expectedHash)) {
            Write-Error "Section '$($section.Key)' missing expected_hash. Skipping."
            $allValid = $false
            continue
        }

        Write-Output "Validating: $destinationPath"

        if (!(Test-Path -LiteralPath $destinationPath)) {
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
