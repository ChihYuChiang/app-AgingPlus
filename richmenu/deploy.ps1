#--Create a richmenu object and upload an image onto LINE server

. './shared.ps1'

#Create object
$body = @"
{
	"size": {
		"width": 800,
		"height": 540
	},
	"selected": true,
	"name": "richmenu 1",
	"chatBarText": "Tap here",
	"areas": [{
		"bounds": {
			"x": 0,
			"y": 0,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "message",
			"label": "1",
			"text": "1"
		}
	}, {
		"bounds": {
			"x": 267,
			"y": 0,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "message",
			"label": "2",
			"text": "2"
		}
	}, {
		"bounds": {
			"x": 534,
			"y": 0,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "message",
			"label": "3",
			"text": "n"
		}
	}, {
		"bounds": {
			"x": 0,
			"y": 270,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "message",
			"label": "4",
			"text": "4"
		}
	}, {
		"bounds": {
			"x": 267,
			"y": 270,
			"width": 266,
			"height": 270
		},
		"action": {  
			"type": "uri",
			"label": "5",
			"uri": "$($config.uri.officialSite)",
			"altUri": {
			   "desktop": "$($config.uri.officialSite)"
			}
		 }
	}, {
		"bounds": {
			"x": 534,
			"y": 270,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "message",
			"label": "6",
			"text": "6"
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