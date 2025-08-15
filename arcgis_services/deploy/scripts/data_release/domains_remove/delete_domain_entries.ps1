#Called to execute add_domains.py using WinRm 

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptPath -Parent
$scriptDir = $scriptDir -replace "\\[^\\]*(?:\\)?$"

Set-Location -path $scriptDir
Write-Output "Working directory : $scriptDir"

$command  = ' -m domains_remove.delete_domain_entries'

Write-Output "Command to execute : $command"

$proc = Start-Process python  -ArgumentList $command -NoNewWindow -PassThru
$handle = $proc.Handle # cache proc.Handle
$proc.WaitForExit();

if ($proc.ExitCode -ne 0) {
    Write-Warning "$_ exited with status code $($proc.ExitCode)"
    throw [System.Exception] "Error executing the python script"
}