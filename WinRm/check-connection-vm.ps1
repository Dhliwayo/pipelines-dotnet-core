$soptions = New-PSSessionOption -SkipCACheck -SkipCNCheck
$secpasswd = ConvertTo-SecureString "TendayiMutsa01" -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("Dhliwayo", $secpasswd) 
$computername = "20.117.169.184"
$computerport = 5986
Enter-PSSession -ComputerName $computername -Port $computerport -Credential $cred -SessionOption $soptions -UseSSL