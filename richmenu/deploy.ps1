. './shared.ps1'
. './clean.ps1'

# Configure client menu
. './config_client.ps1'

# Set as default
Invoke-RestMethod -Uri $($lineUri + 'user/all/richmenu/' + $richmenu.richMenuId) -Method Post -Headers $headers
Write-Host "Set $($richmenu.richMenuId) as default"


# -- Run in PS7 console when debugging
# Set-Location -Path "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\richmenu\"
# pwsh -ExecutionPolicy ByPass -File deploy.ps1