#Adhoc script to gat the latest config files from environments 

$batchManager="D:\inetpub\wwwroot\BatchManager\Web.config"
$batchStatus="D:\inetpub\wwwroot\BatchStatus\Web.config"
$bestAddress="D:\inetpub\wwwroot\BestAddress\Web.config"
$geoassessment="D:\inetpub\wwwroot\Geoassessment\Web.config"
$globalExposure="D:\inetpub\wwwroot\GlobalExposure\Web.config"
$locatorHubWS="D:\inetpub\wwwroot\LocatorHubWS\Web.config"
$perilsPlusWS="D:\inetpub\wwwroot\PerilsPlusWS\Web.config"

$batchServices = "C:\Program Files\Esri UK\Perils and Proximity\BatchServices\batch.config" 
$batchProcessor_Log ="C:\Program Files\Esri UK\Perils and Proximity\BatchServices\BatchProcessor_Log.config"
$batchProcessorService = "C:\Program Files\Esri UK\Perils and Proximity\BatchServices\BatchProcessorService.exe.config" 
$batchSubmissionService = "C:\Program Files\Esri UK\Perils and Proximity\BatchServices\BatchSubmissionService.exe.config" 
$MQListener = "C:\Program Files (x86)\Esri UK\Perils and Proximity\MQListener\MQListener.exe.config"
$batchSubmission_log="C:\Program Files (x86)\Esri UK\Perils and Proximity\BatchServices\BatchSubmission_log.config" 
$batchWebTestHarness="C:\Program Files (x86)\Esri UK\Perils and Proximity\TestHarness\BatchServicesTestHarness\BatchWebTestHarness.exe.config"
$create_Message="C:\Program Files (x86)\Esri UK\Perils and Proximity\TestHarness\MQTestHarnesses\Create_Message.exe.config"
$tEst_App="C:\Program Files (x86)\Esri UK\Perils and Proximity\TestHarness\MQTestHarnesses\TEst_App.exe.config"

$environments = @(
    [pscustomobject]@{EnvironmentName='staging'; Computername='LWUKWVRI53.opd.ads.uk.rsa-ins.com'; Pnp_service_account_name="OPD\GRAUData";   Pnp_service_account_password="Unitedkingdom@1234567890"}
    [pscustomobject]@{EnvironmentName='fint'; Computername='lwukwvri52.opd.ads.uk.rsa-ins.com'; Pnp_service_account_name="OPD\GRAUData";   Pnp_service_account_password="Unitedkingdom@1234567890"}
    [pscustomobject]@{EnvironmentName='preprod'; Computername='LWUKWVRI55.opd.ads.uk.rsa-ins.com'; Pnp_service_account_name="OPD\GRPNPADOPP";   Pnp_service_account_password="TLKF7sYA7bTd&c8GXQ`$S"}
    [pscustomobject]@{EnvironmentName='prod'; Computername='LWUKWVPI255.opd.ads.uk.rsa-ins.com'; Pnp_service_account_name="OPD\GRPNPADOPROD";   Pnp_service_account_password="x7DM6wVz3k8Q46vfvXAv"}
)

foreach ($env in $environments)
{
    try {
        Write-Host "Env: $($env.EnvironmentName), computer: $($env.Computername), acc: $($env.Pnp_service_account_name), pass: $($env.Pnp_service_account_password)"

        $batchManagerDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchManager\Web.config"
        $batchStatusDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchStatus\Web.config"
        $bestAddressDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BestAddress\Web.config"
        $geoassessmentDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\Geoassessment\Web.config"
        $globalExposureDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\GlobalExposure\Web.config"
        $locatorHubWSDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\LocatorHubWS\Web.config"
        $perilsPlusWSDest="\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\PerilsPlusWS\Web.config"
    
        $batchServicesDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\batch.config"; 
        $batchProcessor_LogDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchProcessor_Log.config"; 
        $batchProcessorServiceDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchProcessorService.exe.config";
        $batchSubmissionServiceDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchSubmissionService.exe.config";
        $MQListenerDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\MQListener.exe.config";   
        $batchSubmission_logDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchSubmission_log.config";
        $batchWebTestHarnessDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\BatchWebTestHarness.exe.config";
        $create_MessageDest = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\Create_Message.exe.config";
        $tEst_Ap = "\\lwukwvri53\d$\Transfer\LawrenceD\PnpConfig\$($env.EnvironmentName)\TEst_App.exe.config";
    
        $soptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
        $secpasswd = ConvertTo-SecureString $env.Pnp_service_account_password -AsPlainText -Force
        $cred = New-Object System.Management.Automation.PSCredential ($env.Pnp_service_account_name, $secpasswd) 
    
        $session = New-PSSession -ComputerName $env.Computername -Port 5985 -Credential $cred -SessionOption $soptions

        Write-Host "Session established on environment: $($env.EnvironmentName)"
    
        Copy-Item $batchManager -Destination $batchManagerDest -FromSession $session  -Recurse  -Force
        Copy-Item $batchProcessor_Log -Destination $batchProcessor_LogDest -FromSession $session  -Recurse  -Force
        Copy-Item $batchStatus -Destination $batchStatusDest -FromSession $session  -Recurse  -Force
        Copy-Item $bestAddress -Destination $bestAddressDest -FromSession $session  -Recurse  -Force
        Copy-Item $geoassessment -Destination $geoassessmentDest -FromSession $session  -Recurse  -Force
        Copy-Item $globalExposure -Destination $globalExposureDest -FromSession $session  -Recurse  -Force
        Copy-Item $locatorHubWS -Destination $locatorHubWSDest -FromSession $session  -Recurse  -Force
        Copy-Item $perilsPlusWS -Destination $perilsPlusWSDest -FromSession $session  -Recurse  -Force
    
        Copy-Item $batchServices -Destination $batchServicesDest -FromSession $session  -Recurse  -Force
        Copy-Item $batchProcessorService  -Destination $batchProcessorServiceDest -FromSession $session  -Recurse  -Force
        Copy-Item $batchSubmissionService  -Destination $batchSubmissionServiceDest -FromSession $session  -Recurse  -Force
        Copy-Item $MQListener  -Destination $MQListenerDest -FromSession $session  -Recurse  -Force
        #Copy-Item $batchSubmission_log  -Destination $batchSubmission_logDest -FromSession $session  -Recurse  -Force
        Copy-Item $batchWebTestHarness  -Destination $batchWebTestHarnessDest -FromSession $session  -Recurse  -Force
        Copy-Item $create_Message  -Destination $create_MessageDest -FromSession $session  -Recurse  -Force
        Copy-Item $tEst_App  -Destination $tEst_Ap -FromSession $session  -Recurse  -Force
    
        Remove-PSSession -Session  $session        
    }
    catch {
        Write-Output $_
        Write-Host "Env: $($env.EnvironmentName), error...!" -ForegroundColor Red 
    }
}

