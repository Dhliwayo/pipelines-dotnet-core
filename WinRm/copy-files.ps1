$soptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
$secpasswd = ConvertTo-SecureString "TendayiMutsa01" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("Dhliwayo", $secpasswd) 
$computername = "20.117.169.184"
$computerport = 5986
$sourceDirectory='D:\Dhliwayo\PD\pipelines-dotnet-core\staging'
$destinationFolder='C:\PnPConfigsDeployment\staging'

Write-Host "Copying files source directory:  $sourceDirectory, destination directory:  $destinationFolder"


$session = New-PSSession -ComputerName $computername -Port $computerport -Credential $cred -UseSSL -SessionOption $soptions

Copy-Item $sourceDirectory\* -Destination $destinationFolder -ToSession $session  -Recurse  -Force