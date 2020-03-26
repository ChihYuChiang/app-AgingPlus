# Path contains build folder and lambda.py file
$path = $PSScriptRoot + '\'


# Move content to build folder
Copy-Item $($path + '*.py') `
	-Destination $($path + 'build')


# Delete old build
Remove-Item –path $($path + 'LineBot.zip')


# Make new build
Set-Location "C:\Program Files\7-Zip\"
.\7z a $($path + 'LineBot.zip') `
	$($path + 'build\*')


# Update Lambda
aws lambda update-function-code `
    --function-name LineBot `
    --zip-file $("fileb://" + $path + "LineBot.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'
