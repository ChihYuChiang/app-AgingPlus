#Path contains build folder and lambda.py file
$path = "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\lambda_airtable\"

Copy-Item $($path + 'lambda.js') `
	-Destination $($path + 'build')

Compress-Archive -Path $($path + 'build\*'), $($path + 'node_modules') `
	-destinationpath $($path + 'Airtable.zip') `
	-compressionlevel optimal -Force

aws lambda update-function-code `
    --function-name Airtable `
    --zip-file $("fileb://" + $path + "Airtable.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'