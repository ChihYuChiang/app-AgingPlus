# Set `targetDate` from parameter input with default to today (local time)
# Set `logGroupName` from parameter input with default to LineBot
Param ( `
    [String]$targetDateStr=$(Get-Date -Format "yyyy/MM/dd"), `
    [String]$logGroupName='/aws/lambda/LineBot', `
    [String]$source='s3' `
)
$targetDate = [DateTime]::parseexact($targetDateStr, 'yyyy/MM/dd', $null)
Write-Host "Set target date to $targetDateStr."


# Get log and save to temp file
$path = $PSScriptRoot + '\'
. $($path + 'getlog.ps1')

Switch ($source) {
    'cw' {
        $tempFile = GetLog-CloudWatch -targetDate $targetDate -logGroupName $logGroupName
        break
    }
    's3' {}
    Default {
        $tempFile = GetLog-s3 -targetDate $targetDate -logGroupName $logGroupName
    }
}


# TODO: Pass the log events to the python parser
python parselog.py $tempFile


# Clean up the tmp file
Remove-Item -Path $tempFile
Write-Host 'Parsed and output log file to XXX.'