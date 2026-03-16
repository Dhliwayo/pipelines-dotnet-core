param(
    [string[]]$Users = @('gr\user_1', 'gr\user_2'),
    [string]$DriveLetter = 'D:'
)

$scriptPath = $MyInvocation.MyCommand.Path
$logPath = [System.IO.Path]::ChangeExtension($scriptPath, '.txt')

if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}

Start-Transcript -Path $logPath -Force

Write-Host "===== D Drive Access Check ====="
Write-Host "Server: $(hostname)"
Write-Host "Drive:  $DriveLetter"
Write-Host "Date:   $(Get-Date)"
Write-Host ""

$adAvailable = $true
try {
    Import-Module ActiveDirectory -ErrorAction Stop
} catch {
    $adAvailable = $false
    Write-Host "WARNING: ActiveDirectory module not available. Group membership will not be checked."
    Write-Host ""
}

foreach ($user in $Users) {
    Write-Host "====================================="
    Write-Host "User: $user"
    Write-Host "-------------------------------------"

    $domain = $null
    $sam    = $user
    if ($user -like "*\*") {
        $parts  = $user.Split('\', 2)
        $domain = $parts[0]
        $sam    = $parts[1]
    }

    if ($adAvailable) {
        try {
            $adUser = Get-ADUser -Identity $sam -ErrorAction Stop
            $groups = Get-ADPrincipalGroupMembership -Identity $adUser | Select-Object -ExpandProperty Name

            Write-Host "Groups:"
            if ($groups -and $groups.Count -gt 0) {
                $groups | ForEach-Object { Write-Host "  $_" }
            } else {
                Write-Host "  (No groups found or user not in any groups.)"
            }
        } catch {
            Write-Host "Could not retrieve group membership for $user. Error: $($_.Exception.Message)"
            $groups = @()
        }
    } else {
        $groups = @()
    }

    Write-Host ""
    Write-Host "NTFS permissions on $DriveLetter for $user and their groups:"
    Write-Host "--------------------------------------------------------"

    try {
        $acl = Get-Acl -Path $DriveLetter

        $aces = $acl.Access | Where-Object {
            $id = $_.IdentityReference.Value
            $idSam = $id.Split('\')[-1]

            ($id -ieq $user) -or
            ($idSam -ieq $sam) -or
            ($groups -contains $idSam)
        }

        if ($aces -and $aces.Count -gt 0) {
            $aces | Select-Object IdentityReference, FileSystemRights, AccessControlType, InheritanceFlags, PropagationFlags |
                Format-Table -AutoSize
        } else {
            Write-Host "  No matching explicit ACEs found on $DriveLetter for $user or their groups."
        }
    } catch {
        Write-Host "Could not read ACL for $DriveLetter. Error: $($_.Exception.Message)"
    }

    Write-Host ""
}

Write-Host "===== Check complete ====="
Stop-Transcript

param(
    [string[]]$Users = @('gr\user_1', 'gr\user_2'),
    [string]$DriveLetter = 'D:'
)

$scriptPath = $MyInvocation.MyCommand.Path
$logPath = [System.IO.Path]::ChangeExtension($scriptPath, '.txt')

if (Test-Path $logPath) {
    Remove-Item $logPath -Force
}

Start-Transcript -Path $logPath -Force

Write-Host "===== D Drive Access Check ====="
Write-Host "Server: $(hostname)"
Write-Host "Drive:  $DriveLetter"
Write-Host "Date:   $(Get-Date)"
Write-Host ""

$adAvailable = $true
try {
    Import-Module ActiveDirectory -ErrorAction Stop
} catch {
    $adAvailable = $false
    Write-Host "WARNING: ActiveDirectory module not available. Group membership will not be checked."
    Write-Host ""
}

foreach ($user in $Users) {
    Write-Host "====================================="
    Write-Host "User: $user"
    Write-Host "-------------------------------------"

    $domain = $null
    $sam    = $user
    if ($user -like "*\*") {
        $parts  = $user.Split('\', 2)
        $domain = $parts[0]
        $sam    = $parts[1]
    }

    if ($adAvailable) {
        try {
            $adUser = Get-ADUser -Identity $sam -ErrorAction Stop
            $groups = Get-ADPrincipalGroupMembership -Identity $adUser | Select-Object -ExpandProperty Name

            Write-Host "Groups:"
            if ($groups -and $groups.Count -gt 0) {
                $groups | ForEach-Object { Write-Host "  $_" }
            } else {
                Write-Host "  (No groups found or user not in any groups.)"
            }
        } catch {
            Write-Host "Could not retrieve group membership for $user. Error: $($_.Exception.Message)"
            $groups = @()
        }
    } else {
        $groups = @()
    }

    Write-Host ""
    Write-Host "NTFS permissions on $DriveLetter for $user and their groups:"
    Write-Host "--------------------------------------------------------"

    try {
        $acl = Get-Acl -Path $DriveLetter

        $aces = $acl.Access | Where-Object {
            $id = $_.IdentityReference.Value
            $idSam = $id.Split('\')[-1]

            ($id -ieq $user) -or
            ($idSam -ieq $sam) -or
            ($groups -contains $idSam)
        }

        if ($aces -and $aces.Count -gt 0) {
            $aces | Select-Object IdentityReference, FileSystemRights, AccessControlType, InheritanceFlags, PropagationFlags |
                Format-Table -AutoSize
        } else {
            Write-Host "  No matching explicit ACEs found on $DriveLetter for $user or their groups."
        }
    } catch {
        Write-Host "Could not read ACL for $DriveLetter. Error: $($_.Exception.Message)"
    }

    Write-Host ""
}

Write-Host "===== Check complete ====="
Stop-Transcript

