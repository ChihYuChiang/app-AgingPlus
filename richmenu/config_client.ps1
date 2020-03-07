# TODO: Dif rich menu for client, non-client, graduated client
# -- Create a richmenu object and upload an image onto LINE server
# Create object
$body = @"
{
	"size": {
		"width": 800,
		"height": 540
	},
	"selected": true,
	"name": "richmenu 1",
	"chatBarText": "樂齡運動小幫手",
	"areas": [{
		"bounds": {
			"x": 0,
			"y": 0,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "postback",
			"label": "1",
			"data": "action=class_history",
			"displayText": "運動週報"
		}
	}, {
		"bounds": {
			"x": 267,
			"y": 0,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "postback",
			"label": "2",
			"data": "action=homework",
			"displayText": "課後練習"
		}
	}, {
		"bounds": {
			"x": 534,
			"y": 0,
			"width": 266,
			"height": 270
		},
		"action": {
			"type": "postback",
			"label": "3",
			"data": "action=next_class",
			"displayText": "下次上課資訊"
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
			"text": "運動小學堂 施工中"
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
			"type": "datetimepicker",
			"label": "6",
			"mode": "datetime",
			"data": "action=reschedule_class"
		}
	}]
}
"@

$richmenu = Invoke-RestMethod -Uri $($lineUri + 'richmenu/') -Method Post -Headers $headers -Body ([System.Text.Encoding]::UTF8.GetBytes($body)) # Use PS 6 + Transform to byte code to avoid Chinese encoding issue
Write-Host "Created $($richmenu.richMenuId)"

# Upload image
$headers['Content-Type'] = 'image/jpeg'
$filePath = $path + 'richmenu\public\img_client.jpg'
Invoke-RestMethod -Uri $($lineUri + 'richmenu/' + $richmenu.richMenuId + '/content') -Method Post -Headers $headers -InFile $filePath
Write-Host "Uploaded image for $($richmenu.richMenuId)"
