param(
    [string]$SharePath = '\\machine1\$d'
)

$scriptPath = $MyInvocation.MyCommand.Path
$logPath = [System.IO.Path]::ChangeExtension($scriptPath, '.txt')

if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}

Start-Transcript -Path $logPath -Force

Write-Host "===== Shared D: Access Check ====="
Write-Host "Server:    $(hostname)"
Write-Host "User:      $([Environment]::UserName)"
Write-Host "SharePath: $SharePath"
Write-Host "Date:      $(Get-Date)"
Write-Host ""

$hasRead = $false
$hasWrite = $false
$readError = $null
$writeError = $null

Write-Host "Testing READ access (listing contents)..."
try {
    Get-ChildItem -Path $SharePath -ErrorAction Stop | Out-Null
    $hasRead = $true
    Write-Host "  READ test: SUCCESS"
} catch {
    $readError = $_.Exception.Message
    Write-Host "  READ test: FAILED"
    Write-Host "  Error: $readError"
}

Write-Host ""
Write-Host "Testing WRITE access (create/delete temp file)..."

$tempFileName = "access_test_{0}_{1}.tmp" -f $env:COMPUTERNAME, $PID
$tempFilePath = Join-Path -Path $SharePath -ChildPath $tempFileName

try {
    "access test" | Out-File -FilePath $tempFilePath -Force -ErrorAction Stop
    Remove-Item $tempFilePath -Force -ErrorAction Stop
    $hasWrite = $true
    Write-Host "  WRITE test: SUCCESS"
} catch {
    $writeError = $_.Exception.Message
    Write-Host "  WRITE test: FAILED"
    Write-Host "  Error: $writeError"
}

Write-Host ""
Write-Host "===== SUMMARY ====="
Write-Host "Readable: $hasRead"
if (-not $hasRead -and $readError) {
    Write-Host "  Read error: $readError"
}
Write-Host "Writable: $hasWrite"
if (-not $hasWrite -and $writeError) {
    Write-Host "  Write error: $writeError"
}

Write-Host ""
Write-Host "===== Check complete ====="
Stop-Transcript

