# Deploy config files 

# Todo 
# 
# - compare checksums, notify and skip if identical 
# - rollback option 


# Globals 

# $configs = @{ 
    # TestConfig        = @{Source = "source\web.txt"; Target = "C:\Users\f33124\Documents\test\deploy\target\webno.txt" };
    # AnotherTestConfig = @{Source = "source\web_1.txt"; Target = "C:\Users\f33124\Documents\test\deploy\target\web_1.txt" }
# }

$configs = @{ 
    BatchManager   = @{
        Source = ".\config\BatchManager\web.config"; 
        Target = "D:\inetpub\wwwroot\BatchManager\web.config"
    };
    BatchStatus    = @{
        Source = ".\config\BatchStatus\web.config"; 
        Target = "D:\inetpub\wwwroot\BatchStatus\web.config" 
    };
    BestAddress    = @{
        Source = ".\config\BestAddress\web.config"; 
        Target = "D:\inetpub\wwwroot\BestAddress\web.config" 
    };
    Geoassessment  = @{
        Source = ".\config\Geoassessment\web.config"; 
        Target = "D:\inetpub\wwwroot\Geoassessment\web.config" 
    };
    GlobalExposure = @{
        Source = ".\config\GlobalExposure\web.config"; 
        Target = "D:\inetpub\wwwroot\GlobalExposure\web.config" 
    };
    LocatorHubWS   = @{
        Source = ".\config\LocatorHubWS\web.config"; 
        Target = "D:\inetpub\wwwroot\LocatorHubWS\web.config" 
    };
    PerilsPlusWS   = @{
        Source = ".\config\PerilsPlusWS\web.config"; 
        Target = "D:\inetpub\wwwroot\PerilsPlusWS\web.config" 
    };
    batchconfig    = @{
        Source = ".\config\batch.config"; 
        Target = "C:\Program Files\Esri UK\Perils and Proximity\BatchServices\batch.config" 
    };
    batchprocess   = @{
        Source = ".\config\BatchProcessorService.exe.config"; 
        Target = "C:\Program Files\Esri UK\Perils and Proximity\BatchServices\BatchProcessorService.exe.config" 
    };
    batchsubmit    = @{
        Source = ".\config\BatchSubmissionService.exe.config"; 
        Target = "C:\Program Files\Esri UK\Perils and Proximity\BatchServices\BatchSubmissionService.exe.config" 
    };
    mqlistener     = @{
        Source = ".\config\MQListener.exe.config"; 
        Target = "C:\Program Files (x86)\Esri UK\Perils and Proximity\MQListener\MQListener.exe.config" 
    }
}

$scriptPath = $MyInvocation.MyCommand.Path
$scriptDir = Split-Path $scriptPath -Parent

Set-Location -path $scriptDir
Write-Output "Working directory : $scriptDir"

# Functions


# Logic 

# 1. Backup 

# Create backup folder 

$datetimenow = Get-Date -Format "yyyy-MM-dd-hhmmss"

$backupfolder = "../../../backup_" + $datetimenow

$backuppath = Join-Path -Path $pwd -ChildPath $backupfolder

New-Item -Path $backuppath -ItemType Directory

# 2. Copy target file to backup 
# Skip if target doesn't exist 

Write-Output "Creating backup at $backuppath"

$configs.GetEnumerator() | ForEach-Object {

    If ((Test-Path -Path $_.Value.Target -PathType Leaf) -eq $False) {    
        Write-Output $_.Value.Target " does not exist"
    }
    Else {
        $target_name = Split-Path $_.Value.Target -NoQualifier
        $target_path = Join-Path -Path $backuppath -ChildPath $target_name
        $target_dir = Split-Path $target_path -Parent

        if ((Test-Path $target_dir) -eq $False) {
            New-Item -Path $target_dir -ItemType Directory
        }

        Copy-Item $_.Value.Target -Destination $target_path
    }
}

# 3. Overwrite target file with new source 

Write-Output "Deploying new config files"

$configs.GetEnumerator() | ForEach-Object {

    # Check whether target and source exists before trying to copy 
    Write-Output "Processing: " $_.Value.Target

    If ((Test-Path -Path $_.Value.Source -PathType Leaf) -eq $False) {
        Write-Output " > Input " $_.Value.Source " does not exist"
   }
    ElseIf ((Test-Path -Path $_.Value.Target -PathType Leaf) -eq $False) {
        Write-Output " > Target " $_.Value.Target " does not exist"
    }
    Else {
        Copy-Item $_.Value.Source -Destination $_.Value.Target -force
    }

    # For testing on dev box, we create the destination path if does not exist
	If ((Test-Path -Path $_.Value.Target -PathType Leaf) -eq $False) {
    
		$destinationPath = Split-Path -Path $_.Value.Target 
		
		Write-Output "Creating destination path:  " $destinationPath
		New-Item -Path $destinationPath -ItemType Directory -Force
		
		Copy-Item $_.Value.Source -Destination $_.Value.Target -force
    }
}




