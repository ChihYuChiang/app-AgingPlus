function GetLog-CloudWatch {
    Param ([DateTime]$targetDate, [String]$logGroupName)

    # Compute start and end time (1 particular day) in the format AWS CLI expects
    $unixEpochStart = New-Object DateTime 1970,1,1,0,0,0,([DateTimeKind]::Local)
    $startTime = ($targetDate - $unixEpochStart).TotalMilliseconds
    $endTime = ($targetDate.AddDays(1) - $unixEpochStart).TotalMilliseconds
    Write-Host 'Calculated start and end time.'
    
    # Get log stream name of the latest lambda version
    $describeLogStreams = aws logs describe-log-streams --log-group-name $logGroupName --order-by 'LastEventTime' --descending | ConvertFrom-Json
    $logStreamName = $describeLogStreams.logStreams[0].logStreamName
    Write-Host 'Got latest log stream.'
    
    # Get log of the specified date
    $logEvents = aws logs get-log-events --log-group-name $logGroupName --log-stream-name $logStreamName --start-time $startTime --end-time $endTime | ConvertFrom-Json
    Write-Host 'Downloaded logs.'

    # Save log json to a tmp file
    $tempFile = New-TemporaryFile
    ConvertTo-Json $logEvents.events > $tempFile

    return $tempFile
}


function GetLog-S3 {
    Param ([DateTime]$targetDate, [String]$logGroupName)

    # Search the s3 for log stream folder
    $listObjects = aws s3api list-objects-v2 --bucket 'agingplus-log' --prefix 'aws-lambda-LineBot/2020/3/21/' | ConvertFrom-Json
    If ($listObjects.Contents.Length) {Write-Host 'Found log.'}
    Else {Write-Host 'No log found.'; return}

    # Retrieve the logs and save as json to a tmp file
    $tempFile = New-TemporaryFile
    aws s3api get-object --bucket 'agingplus-log' --key $listObjects.Contents[1].Key $tempFile
    Write-Host 'Downloaded logs.'

    return $tempFile
}