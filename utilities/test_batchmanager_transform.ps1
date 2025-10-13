# Quick test script for BatchManager config transforms
# This script helps you quickly test different environment transforms

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("Production", "PreProd", "Staging")]
    [string]$Environment = "PreProd"
)

$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$rootPath = Split-Path -Parent $scriptPath

# Define paths
$sourceConfig = Join-Path $rootPath "staging\config\BatchManager\Web.config"
$transformConfig = Join-Path $rootPath "staging\config\BatchManager\Web.$Environment.config"
$outputConfig = Join-Path $rootPath "staging\config\BatchManager\Web.Transformed.$Environment.config"

Write-Host "Testing $Environment transformation for BatchManager" -ForegroundColor Cyan
Write-Host ""

# Check if transform file exists
if (-not (Test-Path $transformConfig)) {
    Write-Error "Transform file not found: $transformConfig"
    Write-Host ""
    Write-Host "Available transform files:" -ForegroundColor Yellow
    Get-ChildItem (Join-Path $rootPath "staging\config\BatchManager") -Filter "Web.*.config" | ForEach-Object {
        Write-Host "  - $($_.Name)" -ForegroundColor Yellow
    }
    exit 1
}

# Call the main test transform script
$testScript = Join-Path $scriptPath "test_transform.ps1"
& $testScript -SourceFile $sourceConfig -TransformFile $transformConfig -OutputFile $outputConfig

