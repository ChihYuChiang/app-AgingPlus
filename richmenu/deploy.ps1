#--Create a richmenu object and upload an image onto LINE server

. './shared.ps1'

#Create object
$body = @"
{
	"size": {
		"width": 800,
		"height": 540
	},
	"selected": false,
	"name": "Nice richmenu",
	"chatBarText": "Tap here",
	"areas": [{
		"bounds": {
			"x": 0,
			"y": 0,
			"width": 800,
			"height": 540
		},
		"action": {
			"type": "postback",
			"data": "action=buy&itemid=123"
		}
	}]
}
"@
$richmenu = Invoke-RestMethod -Uri $($lineUri + 'richmenu/') -Method Post -Headers $headers -Body $body
Write-Host "Created $($richmenu.richMenuId)"

#Upload image
$headers['Content-Type'] = 'image/jpeg'
$filePath = $path + 'richmenu\public\img.jpg'
Invoke-RestMethod -Uri $($lineUri + 'richmenu/' + $richmenu.richMenuId + '/content') -Method Post -Headers $headers -InFile $filePath
Write-Host "Uploaded image for $($richmenu.richMenuId)"

#Set as default
Invoke-RestMethod -Uri $($lineUri + 'user/all/richmenu/' + $richmenu.richMenuId) -Method Post -Headers $headers
Write-Host "Set $($richmenu.richMenuId) as default"