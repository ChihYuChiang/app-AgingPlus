#Path contains build folder and lambda.py file
$path = "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\lambda_linebot\"

Copy-Item $($path + 'lambda.py') `
	-Destination $($path + 'build')

Set-Location "C:\Program Files\7-Zip\"
.\7z a $($path + 'LineBot.zip') `
	$($path + 'build\*')

aws lambda update-function-code `
    --function-name LineBot `
    --zip-file $("fileb://" + $path + "LineBot.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'