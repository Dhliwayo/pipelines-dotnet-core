function Get-AuditRuleForFile {
    $auditRuleArguments =   'Everyone'              <# identity #>,
                            'ExecuteFile, Traverse' <# fileSystemRights #>,
                            'Success'               <# flags #>
    $auditRule = New-Object System.Security.AccessControl.FileSystemAuditRule($auditRuleArguments)

return $auditRule
}

function Set-FileAuditRule {
    param (
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [string]$file,
        [Parameter(Mandatory = $true)]
        [ValidateNotNullOrEmpty()]
        [System.Security.AccessControl.FileSystemAuditRule]$auditRule
    )

    $existingAcl = Get-Acl -Path $file
    $existingAcl.AddAuditRule($auditRule) | Out-Null
    Set-Acl -Path $file -AclObject $existingAcl
}

$newAuditRule = Get-AuditRuleForFile

# Visual Studio C++ Redistributable DLLs from WinSxS (all versions)
Get-ChildItem "$ENV:SystemRoot\WinSxS" -filter '*.dll' -ErrorAction SilentlyContinue -Recurse |
Where-Object FullName -IMatch 'microsoft\.vc[0-9]+' |
ForEach-Object {
    Set-FileAuditRule $_.FullName $newAuditRule
}

# Visual Studio C++ Redistributable DLLs from System32 and SysWOW64 (all versions)
# Updated regex to match all VC++ versions (80, 90, 100, 110, 120, 140, 150, 160, etc.)
$languageCodes = 'chs|cht|deu|enu|esn|fra|ita|jpn|kor|rus'
$versions = '([0-9]+0)'  # Matches any version ending in 0 (80, 90, 100, 110, etc.)
$regex = "^((atl|msvc[pr]|vcamp|vccorlib|vcomp)$versions|mfc$versions(u|$languageCodes)?|mfcm$versions(u)?)\.dll$"
Get-ChildItem "$ENV:SystemRoot\SysWOW64","$ENV:SystemRoot\System32" -filter '*.dll' |
Where-Object Name -imatch $regex |
ForEach-Object {
    Set-FileAuditRule $_.FullName $newAuditRule
}

# Additional search for newer VC++ redistributables that might use different naming patterns
# This covers VC++ 2015, 2017, 2019, 2022 and beyond
$modernVcPatterns = @(
    'vcruntime\d+\.dll',
    'msvcp\d+\.dll',
    'vccorlib\d+\.dll',
    'vcomp\d+\.dll',
    'atl\d+\.dll',
    'mfc\d+\.dll',
    'mfcm\d+\.dll',
    'mfcs\d+\.dll'
)

foreach ($pattern in $modernVcPatterns) {
    Get-ChildItem "$ENV:SystemRoot\SysWOW64","$ENV:SystemRoot\System32" -filter '*.dll' |
    Where-Object Name -imatch "^$pattern$" |
    ForEach-Object {
        Set-FileAuditRule $_.FullName $newAuditRule
    }
}