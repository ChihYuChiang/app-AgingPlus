# Path contains build folder and lambda.py file
$path = "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\lambda_log\"

Copy-Item $($path + '*.js') `
	-Destination $($path + 'build')

# Use 7z to compress instead of powershell (which sucks) to make the file path compatible in linux systems
Set-Location "C:\Program Files\7-Zip\"
.\7z u $($path + 'Log.zip') `
	$($path + 'build\*') $($path + 'node_modules')

aws lambda update-function-code `
    --function-name Log `
    --zip-file $("fileb://" + $path + "Log.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'