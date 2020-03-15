# Store only LineBot logs

$path = Get-Location
Write-Host $PSScriptRoot

# . C:\Users\Anirban\Desktop\Tester.ps1
# add 1 2

# Set `targetDate` from parameter input with default to today (local time)
Param ([String]$targetDateStr=$(Get-Date -Format "yyyy/MM/dd"))
$targetDate = [datetime]::parseexact($targetDateStr, 'yyyy/MM/dd', $null)
Write-Host "Set target date to $targetDateStr."

# Save log json to a tmp file
$TempFile = New-TemporaryFile
ConvertTo-Json $logEvents.events > $TempFile

# TODO: Pass the log events to the python parser
python parselog.py $TempFile

# Clean up the tmp file
Remove-Item -Path $TempFile
Write-Host 'Parsed and output log file to XXX.'