# Requires: PowerShell 5+
param(
    [Parameter(Mandatory=$true)][string]$RootPath,
    [Parameter(Mandatory=$true)][string]$FileGlob,
    [Parameter(Mandatory=$false)][string]$TokenPrefix = "__",
    [Parameter(Mandatory=$false)][string]$TokenSuffix = "__"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "Token replacement starting in: $RootPath for pattern: $FileGlob"

function Get-TokenRegex {
    param(
        [string]$name
    )
    $escapedPrefix = [Regex]::Escape($TokenPrefix)
    $escapedSuffix = [Regex]::Escape($TokenSuffix)
    return "$escapedPrefix$name$escapedSuffix"
}

function Replace-FileTokens {
    param(
        [System.IO.FileInfo]$file
    )

    $content = Get-Content -LiteralPath $file.FullName -Raw

    # Build token map from all environment variables in the current process (Azure DevOps exposes variable group as env vars)
    $envMap = [System.Collections.Generic.Dictionary[string,string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($envName in [Environment]::GetEnvironmentVariables().Keys) {
        $envValue = [Environment]::GetEnvironmentVariable([string]$envName)
        if ($null -ne $envValue -and $envValue -ne '') {
            $envMap[$envName] = $envValue
        }
    }

    $replacements = 0
    foreach ($kvp in $envMap.GetEnumerator()) {
        $token = (Get-TokenRegex -name $kvp.Key)
        if ($content -match [Regex]::Escape($token)) {
            $before = $content
            $content = $content -replace [Regex]::Escape($token), [System.Text.RegularExpressions.Regex]::Escape($kvp.Value).Replace('\\','\\').Replace('$','$$')
            if ($content -ne $before) { $replacements++ }
        }
    }

    if ($replacements -gt 0) {
        Set-Content -LiteralPath $file.FullName -Value $content -NoNewline
        Write-Host "Replaced $replacements token(s) in $($file.FullName)"
    } else {
        Write-Host "No tokens replaced in $($file.FullName)"
    }
}

Get-ChildItem -Path $RootPath -Recurse -File -Include $FileGlob |
    ForEach-Object { Replace-FileTokens -file $_ }

Write-Host "Token replacement completed."


