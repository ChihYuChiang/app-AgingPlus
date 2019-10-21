#Path contains build folder and lambda.py file
$path = "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\lambda_line\"

Copy-Item $($path + 'lambda.py') `
	-Destination $($path + 'build')

Compress-Archive -Path $($path + 'build\*') `
	-destinationpath $($path + 'Line.zip') `
	-compressionlevel optimal -Force

aws lambda update-function-code `
    --function-name Line `
    --zip-file $("fileb://" + $path + "Line.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'