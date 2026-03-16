param(
    [switch]$IncludeManagementTools = $true,
    [switch]$IncludeCommonFeatures = $true
)

$scriptPath = $MyInvocation.MyCommand.Path
$logPath = [System.IO.Path]::ChangeExtension($scriptPath, '.txt')

if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}

Start-Transcript -Path $logPath -Force

Write-Host "===== Enable IIS on Windows Server 2025 ====="
Write-Host "Server: $(hostname)"
Write-Host "User:   $([Environment]::UserName)"
Write-Host "Date:   $(Get-Date)"
Write-Host ""

function Test-IsServerCore {
    try {
        $edition = (Get-ItemProperty -Path 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion' -Name InstallationType -ErrorAction Stop).InstallationType
        return ($edition -eq 'Server Core')
    } catch {
        return $false
    }
}

Write-Host "Checking OS information..."
$os = Get-CimInstance -ClassName Win32_OperatingSystem
Write-Host "  Caption: $($os.Caption)"
Write-Host "  Version: $($os.Version)"
Write-Host "  Build:   $($os.BuildNumber)"
Write-Host ""

if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "ERROR: This script must be run in an elevated (Run as administrator) PowerShell session."
    Write-Host "Exiting."
    Stop-Transcript
    exit 1
}

$isCore = Test-IsServerCore
Write-Host "Installation type: $(if ($isCore) { 'Server Core' } else { 'Desktop Experience' })"
Write-Host ""

Write-Host "Checking if the ServerManager module is available..."
try {
    Import-Module ServerManager -ErrorAction Stop
    $hasServerManager = $true
    Write-Host "  ServerManager module loaded."
} catch {
    $hasServerManager = $false
    Write-Host "  ServerManager module NOT available. Falling back to DISM."
}

Write-Host ""
Write-Host "Checking current IIS state..."
try {
    if ($hasServerManager) {
        $webRole = Get-WindowsFeature -Name Web-Server -ErrorAction Stop
        Write-Host "  IIS installed: $($webRole.Installed)"
    } else {
        $output = dism.exe /online /Get-Features /Format:Table | Select-String -Pattern 'IIS-WebServer\s+\w+'
        if ($output) {
            $state = ($output -split '\s+')[-1]
            Write-Host "  IIS state (DISM): $state"
        } else {
            Write-Host "  Could not determine IIS state via DISM."
        }
    }
} catch {
    Write-Host "  Failed to query IIS state: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "Starting IIS installation..."

if ($hasServerManager) {
    $features = @('Web-Server')

    if ($IncludeCommonFeatures) {
        $features += @(
            'Web-Common-Http',   # Static/Default/DirBrowse/HttpErrors
            'Web-Default-Doc',
            'Web-Dir-Browsing',
            'Web-Http-Errors',
            'Web-Static-Content',
            'Web-Http-Redirect',
            'Web-Health',
            'Web-Http-Logging',
            'Web-Log-Libraries',
            'Web-Request-Monitor'
        )
    }

    if ($IncludeManagementTools -and -not $isCore) {
        $features += @(
            'Web-Mgmt-Tools',
            'Web-Mgmt-Console'
        )
    }

    Write-Host "Installing features:"
    $features | Sort-Object -Unique | ForEach-Object { Write-Host "  $_" }
    Write-Host ""

    try {
        $result = Install-WindowsFeature -Name ($features | Sort-Object -Unique) -IncludeManagementTools:$IncludeManagementTools.IsPresent -ErrorAction Stop
        Write-Host "Installation success: $($result.Success)"
        Write-Host "Exit code: $($result.ExitCode)"
    } catch {
        Write-Host "ERROR: Install-WindowsFeature failed: $($_.Exception.Message)"
    }
} else {
    $featureName = 'IIS-WebServerRole'
    Write-Host "Using DISM to enable feature: $featureName"
    try {
        $dismArgs = "/online /Enable-Feature /FeatureName:$featureName /All /NoRestart"
        Write-Host "Running: dism.exe $dismArgs"
        $proc = Start-Process -FilePath dism.exe -ArgumentList $dismArgs -NoNewWindow -PassThru -Wait
        Write-Host "DISM exit code: $($proc.ExitCode)"
        if ($proc.ExitCode -eq 0) {
            Write-Host "IIS installation via DISM completed successfully."
        } else {
            Write-Host "IIS installation via DISM returned a non-zero exit code."
        }
    } catch {
        Write-Host "ERROR: DISM installation failed: $($_.Exception.Message)"
    }
}

Write-Host ""
Write-Host "Verifying that the W3SVC (World Wide Web Publishing Service) is present..."
try {
    $svc = Get-Service -Name W3SVC -ErrorAction Stop
    Write-Host "  Service status: $($svc.Status)"
    if ($svc.Status -ne 'Running') {
        Write-Host "  Attempting to start W3SVC..."
        Start-Service -Name W3SVC -ErrorAction Stop
        Write-Host "  W3SVC started."
    }
} catch {
    Write-Host "  Could not query or start W3SVC: $($_.Exception.Message)"
}

Write-Host ""
Write-Host "===== IIS enablement script completed ====="
Stop-Transcript

