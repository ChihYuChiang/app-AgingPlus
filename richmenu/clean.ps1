# -- Delete all richmenu objectson LINE server
$richmenuList = Invoke-RestMethod -Uri $($lineUri + 'richmenu/list') -Method Get -Headers $headers
foreach ($richmenu in $richmenuList.richmenus) {
    Invoke-RestMethod -Uri $($lineUri + 'richmenu/' + $richmenu.richMenuId) -Method Delete -Headers $headers
    Write-Host "Deleted $($richmenu.richMenuId)"
}