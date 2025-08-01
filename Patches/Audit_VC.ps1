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

# Visual Studio Redistributable for 2005 (VC++ 8.0) and 2008 (VC++ 9.0)
Get-ChildItem "$ENV:SystemRoot\WinSxS\Fusion" -filter '*.dll' -ErrorAction SilentlyContinue -Recurse |
Where-Object FullName -IMatch 'microsoft\.vc[89]0' |
ForEach-Object {
    Set-FileAuditRule $_.FullName $newAuditRule
}

# Visual Studio Redistributable for 2010 (VC++ 10.0), 2012 (VC++ 11.0) and 2013 (VC++ 12.0)
$languageCodes = 'chs|cht|deu|enu|esn|fra|ita|jpn|kor|rus'
$versions = '(1[012]0)'
$regex = "^((atl|msvc[pr]|vcamp|vccorlib|vcomp)$versions|mfc$versions(u|$languageCodes)?|mfcm$versions(u)?)\.dll$"
Get-ChildItem "$ENV:SystemRoot\SysWOW64","$ENV:SystemRoot\System32" -filter '*.dll' |
Where-Object Name -imatch $regex |
ForEach-Object {
    Set-FileAuditRule $_.FullName $newAuditRule
}