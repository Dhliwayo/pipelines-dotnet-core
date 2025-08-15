# Create checksums for a list of file geodatabases

$Fgdbs = @(
    
    "D:\Galaxy Database\FGDB\base_a.gdb",
	"D:\esriuk\FGDB\PERILS_A.gdb"
)

Function Get-Fgdb-Hash {
    
    param (
        
        $FgdbPath
        
    )
    
    # https://stackoverflow.com/a/64468867
    $HashString = (Get-ChildItem $FgdbPath -Recurse | Get-FileHash -Algorithm MD5).Hash | Out-String
    $FgdbHash = (Get-FileHash -InputStream ([IO.MemoryStream]::new([char[]]$HashString))).Hash
    
    Write-Output $FgdbPath $FgdbHash

}

ForEach ($gdb in $Fgdbs) {
    
    Get-Fgdb-Hash -FgdbPath $gdb

}

Read-Host "Press enter to exit..."