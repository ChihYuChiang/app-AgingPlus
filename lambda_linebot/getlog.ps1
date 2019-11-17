#Set `targetDate` from parameter input with default to today (local time)
Param([String]$targetDateStr=$(Get-Date -Format "yyyy/MM/dd"))
$targetDate = [datetime]::parseexact($targetDateStr, 'yyyy/MM/dd', $null)

#Compute start and end time (1 particular day) in the format AWS CLI expects
$unixEpochStart = New-Object DateTime 1970,1,1,0,0,0,([DateTimeKind]::Local)
$startTime = ($targetDate - $unixEpochStart).TotalMilliseconds
$endTime = ($targetDate.AddDays(1) - $unixEpochStart).TotalMilliseconds

#Get log stream name of the latest lambda version
$logGroupName = '/aws/lambda/LineBot'
$describeLogStreams = aws logs describe-log-streams --log-group-name $logGroupName --order-by 'LastEventTime' --descending | ConvertFrom-Json
$logStreamName = $describeLogStreams.logStreams[0].logStreamName

#Get log of the specified date
$logEvents = aws logs get-log-events --log-group-name $logGroupName --log-stream-name $logStreamName --start-time $startTime --end-time $endTime | ConvertFrom-Json
$logEvents.events

#TODO: Pass the log events to the python parser