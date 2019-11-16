$path = 'C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\'
$lineUri = 'https://api.line.me/v2/bot/'
Write-Host 'Import $path and $lineUri'

Import-Module powershell-yaml
[string[]]$fileContent = Get-Content $($path + 'ref\credential.yml')
$content = ''
foreach ($line in $fileContent) { $content = $content + "`n" + $line }
$cred = ConvertFrom-YAML $content
[string[]]$fileContent = Get-Content $($path + 'ref\config.yml')
$content = ''
foreach ($line in $fileContent) { $content = $content + "`n" + $line }
$config = ConvertFrom-YAML $content
Write-Host 'Import $cred and $config'

$headers = @{
    'Authorization' = $('Bearer ' + $cred.LINE.channelAccessToken)
    'Content-Type' = 'application/json; charset=utf-8'
}
Write-Host 'Import $headers'