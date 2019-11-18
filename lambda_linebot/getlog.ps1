#Set `targetDate` from parameter input with default to today (local time)
Param([String]$targetDateStr=$(Get-Date -Format "yyyy/MM/dd"))
$targetDate = [datetime]::parseexact($targetDateStr, 'yyyy/MM/dd', $null)
Write-Host "Set target date to $targetDateStr."

#Compute start and end time (1 particular day) in the format AWS CLI expects
$unixEpochStart = New-Object DateTime 1970,1,1,0,0,0,([DateTimeKind]::Local)
$startTime = ($targetDate - $unixEpochStart).TotalMilliseconds
$endTime = ($targetDate.AddDays(1) - $unixEpochStart).TotalMilliseconds
Write-Host 'Calculated start and end time.'

#Get log stream name of the latest lambda version
$logGroupName = '/aws/lambda/LineBot'
$describeLogStreams = aws logs describe-log-streams --log-group-name $logGroupName --order-by 'LastEventTime' --descending | ConvertFrom-Json
$logStreamName = $describeLogStreams.logStreams[0].logStreamName
Write-Host 'Got latest log stream.'

#Get log of the specified date
$logEvents = aws logs get-log-events --log-group-name $logGroupName --log-stream-name $logStreamName --start-time $startTime --end-time $endTime | ConvertFrom-Json
Write-Host 'Downloaded logs.'

#Save log json to a tmp file
$TempFile = New-TemporaryFile
ConvertTo-Json $logEvents.events > $TempFile

#TODO: Pass the log events to the python parser
python parselog.py $TempFile

#Clean up the tmp file
Remove-Item -Path $TempFile
Write-Host 'Parsed and output log file to XXX.'