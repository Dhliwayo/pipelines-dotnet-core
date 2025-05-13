$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptPath -Parent

Set-Location -path $scriptDir
Write-Output "Working directory : $scriptDir"

$scriptFile  = Join-Path -Path $scriptDir -ChildPath 'add_domains.py'

Write-Output "Script to execute : $scriptFile"

Start-Process python -ArgumentList $scriptFile -NoNewWindow 