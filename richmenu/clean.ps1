#--Delete all richmenu objectson LINE server

. './shared.ps1'

$richmenuList = Invoke-RestMethod -Uri $($lineUri + 'list') -Method Get -Headers $headers
foreach ($richmenu in $richmenuList.richmenus) {
    Invoke-RestMethod -Uri $($lineUri + $richmenu.richMenuId) -Method Delete -Headers $headers
    Write-Host "Delete $($richmenu.richMenuId)"
}