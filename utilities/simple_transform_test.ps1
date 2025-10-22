# Simple transform test
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
Write-Host "Source: $sourceConfig" -ForegroundColor Green
Write-Host "Transform: $transformConfig" -ForegroundColor Green
Write-Host "Output: $outputConfig" -ForegroundColor Green
Write-Host ""

# Check if files exist
if (-not (Test-Path $sourceConfig)) {
    Write-Error "Source file not found: $sourceConfig"
    exit 1
}

if (-not (Test-Path $transformConfig)) {
    Write-Error "Transform file not found: $transformConfig"
    exit 1
}

# Load the Microsoft.Web.XmlTransform assembly
$xdtDllPath = Join-Path $scriptPath "Microsoft.Web.XmlTransform.dll"

if (-not (Test-Path $xdtDllPath)) {
    Write-Host "Microsoft.Web.XmlTransform.dll not found. Please run the main test script first to download it." -ForegroundColor Yellow
    exit 1
}

try {
    Add-Type -Path $xdtDllPath
    Write-Host "Loaded Microsoft.Web.XmlTransform library" -ForegroundColor Green
}
catch {
    Write-Error "Failed to load XDT library: $_"
    exit 1
}

# Perform the transformation
try {
    Write-Host "Performing transformation..." -ForegroundColor Cyan
    
    # Load source document
    $sourceDoc = New-Object Microsoft.Web.XmlTransform.XmlTransformableDocument
    $sourceDoc.PreserveWhitespace = $true
    $sourceDoc.Load($sourceConfig)
    
    # Load transform document
    $transformDoc = New-Object Microsoft.Web.XmlTransform.XmlTransformation($transformConfig)
    
    # Apply transformation
    $success = $transformDoc.Apply($sourceDoc)
    
    if ($success) {
        # Save the result
        $sourceDoc.Save($outputConfig)
        Write-Host ""
        Write-Host "✓ Transformation successful!" -ForegroundColor Green
        Write-Host "Output saved to: $outputConfig" -ForegroundColor Green
        
        # Show what changed
        Write-Host ""
        Write-Host "Changes made:" -ForegroundColor Cyan
        Write-Host "- Connection strings updated with tokens" -ForegroundColor White
        Write-Host "- Environment-specific settings added" -ForegroundColor White
        Write-Host "- Debug settings configured for $Environment" -ForegroundColor White
        
        Write-Host ""
        Write-Host "You can now review the transformed file to verify the changes." -ForegroundColor Cyan
    }
    else {
        Write-Error "Transformation failed!"
        exit 1
    }
}
catch {
    Write-Error "Error during transformation: $($_.Exception.Message)"
    exit 1
}
finally {
    if ($transformDoc) {
        $transformDoc.Dispose()
    }
}
