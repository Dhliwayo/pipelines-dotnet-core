$fileName = "./self_signed_certificate.pfx"
$fileContentBytes = Get-Content $fileName -Encoding Byte
$fileContentEncoded = [System.Convert]::ToBase64String($fileContentBytes)
[System.Collections.HashTable]$TableForJSON = @{
    "data"     = $fileContentEncoded;
    "dataType" = "pfx";
    "password" = "Tendayi01";
}
[System.String]$jsonObject = $TableForJSON | ConvertTo-Json
$encoding = [System.Text.Encoding]::UTF8
$jsonEncoded = [System.Convert]::ToBase64String($encoding.GetBytes($jsonObject))
$secret = ConvertTo-SecureString -String $jsonEncoded -AsPlainText -Force
az keyvault secret set --name "secret-self-signed-certificate"  --vault-name "vault-devops-training" --value $secret
