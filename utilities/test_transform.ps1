param(
    [Parameter(Mandatory=$true)]
    [string]$SourceFile,
    
    [Parameter(Mandatory=$true)]
    [string]$TransformFile,
    
    [Parameter(Mandatory=$true)]
    [string]$OutputFile
)

# Function to test if running with admin privileges
function Test-Administrator {
    $user = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal $user
    $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

Write-Host "XML Configuration Transform Test Tool" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Check if source file exists
if (-not (Test-Path $SourceFile)) {
    Write-Error "Source file not found: $SourceFile"
    exit 1
}

# Check if transform file exists
if (-not (Test-Path $TransformFile)) {
    Write-Error "Transform file not found: $TransformFile"
    exit 1
}

Write-Host "Source File:    $SourceFile" -ForegroundColor Green
Write-Host "Transform File: $TransformFile" -ForegroundColor Green
Write-Host "Output File:    $OutputFile" -ForegroundColor Green
Write-Host ""

# Load the Microsoft.Web.XmlTransform assembly
$xdtDllPath = Join-Path $PSScriptRoot "Microsoft.Web.XmlTransform.dll"

if (-not (Test-Path $xdtDllPath)) {
    Write-Host "Microsoft.Web.XmlTransform.dll not found. Attempting to download..." -ForegroundColor Yellow
    
    # Download NuGet package
    $nugetUrl = "https://www.nuget.org/api/v2/package/Microsoft.Web.Xdt/3.1.0"
    $tempZip = Join-Path $env:TEMP "xdt.zip"
    $tempExtract = Join-Path $env:TEMP "xdt_extract"
    
    try {
        Write-Host "Downloading Microsoft.Web.Xdt package..." -ForegroundColor Yellow
        Invoke-WebRequest -Uri $nugetUrl -OutFile $tempZip
        
        # Extract the package
        if (Test-Path $tempExtract) {
            Remove-Item $tempExtract -Recurse -Force
        }
        Expand-Archive -Path $tempZip -DestinationPath $tempExtract
        
        # Copy the DLL to utilities folder
        $dllSource = Join-Path $tempExtract "lib\netstandard2.0\Microsoft.Web.XmlTransform.dll"
        if (Test-Path $dllSource) {
            Copy-Item $dllSource -Destination $xdtDllPath
            Write-Host "Successfully downloaded Microsoft.Web.XmlTransform.dll" -ForegroundColor Green
        } else {
            Write-Error "Could not find DLL in package. Please install manually."
            exit 1
        }
        
        # Cleanup
        Remove-Item $tempZip -Force
        Remove-Item $tempExtract -Recurse -Force
    }
    catch {
        Write-Error "Failed to download XDT library: $_"
        Write-Host ""
        Write-Host "Manual installation steps:" -ForegroundColor Yellow
        Write-Host "1. Download: https://www.nuget.org/packages/Microsoft.Web.Xdt/" -ForegroundColor Yellow
        Write-Host "2. Extract the .nupkg file (it's a zip)" -ForegroundColor Yellow
        Write-Host "3. Copy Microsoft.Web.XmlTransform.dll from lib\netstandard2.0\ to utilities\" -ForegroundColor Yellow
        exit 1
    }
}

# Load the XDT library
try {
    Add-Type -Path $xdtDllPath
    Write-Host "Loaded Microsoft.Web.XmlTransform library" -ForegroundColor Green
}
catch {
    Write-Error "Failed to load XDT library: ...."
    exit 1
}

# Perform the transformation
try {
    Write-Host ""
    Write-Host "Performing transformation..." -ForegroundColor Cyan
    
    # Load source document
    $sourceDoc = New-Object Microsoft.Web.XmlTransform.XmlTransformableDocument
    $sourceDoc.PreserveWhitespace = $true
    $sourceDoc.Load($SourceFile)
    
    # Load transform document
    $transformDoc = New-Object Microsoft.Web.XmlTransform.XmlTransformation($TransformFile)
    
    # Apply transformation
    $success = $transformDoc.Apply($sourceDoc)
    
    if ($success) {
        # Save the result
        $sourceDoc.Save($OutputFile)
        Write-Host ""
        Write-Host "✓ Transformation successful!" -ForegroundColor Green
        Write-Host "Output saved to: $OutputFile" -ForegroundColor Green
        Write-Host ""
        Write-Host "You can now review the transformed file to verify the changes." -ForegroundColor Cyan
        
        # Optionally open in default editor
        $open = Read-Host "Do you want to open the output file? (Y/N)"
        if ($open -eq "Y" -or $open -eq "y") {
            Start-Process $OutputFile
        }
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


