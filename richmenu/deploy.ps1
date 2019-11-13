#--Create a richmenu object and upload an image onto LINE server

. './shared.ps1'

$body = @"
{
	"size": {
		"width": 2500,
		"height": 1686
	},
	"selected": false,
	"name": "Nice richmenu",
	"chatBarText": "Tap here",
	"areas": [{
		"bounds": {
			"x": 0,
			"y": 0,
			"width": 2500,
			"height": 1686
		},
		"action": {
			"type": "postback",
			"data": "action=buy&itemid=123"
		}
	}]
}
"@
Invoke-RestMethod -Uri $lineUri -Method Post -Headers $headers -Body $body