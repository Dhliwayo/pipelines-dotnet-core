$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptPath -Parent

Set-Location -path $scriptDir
Write-Output "Working directory : $scriptDir"

$scriptFile  = Join-Path -Path $scriptDir -ChildPath 'add_domains.py'

Write-Output "Script to execute : $scriptFile"

$proc = Start-Process python -ArgumentList $scriptFile -NoNewWindow -PassThru
$handle = $proc.Handle # cache proc.Handle
$proc.WaitForExit();

if ($proc.ExitCode -ne 0) {
    Write-Warning "$_ exited with status code $($proc.ExitCode)"
    throw [System.Exception] "There was an error executing the python script"
}