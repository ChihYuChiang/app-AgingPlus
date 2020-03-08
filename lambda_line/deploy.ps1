#Path contains build folder and lambda.py file
$path = "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\lambda_line\"

Copy-Item $($path + '*.py') `
	-Destination $($path + 'build')

Set-Location "C:\Program Files\7-Zip\"
.\7z u $($path + 'Line.zip') `
	$($path + 'build\*')

aws lambda update-function-code `
    --function-name Line `
    --zip-file $("fileb://" + $path + "Line.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'