# TODO: Share deployment script
# Path contains build folder and source files
$path = $PSScriptRoot + '\'


# Move content to build folder and install prod dependency
Copy-Item `
	$($path + '*.js'), `
	$($path + 'package.json'), `
	$($path + 'package-lock.json') `
	-Destination $($path + 'build\')
Set-Location $($path + 'build\')
npm install --only=prod


# Delete old build
Remove-Item –path $($path + 'Airtable.zip')


# Make new build
# Use 7z to compress instead of powershell (which sucks) to make the file path compatible in linux systems
Set-Location "C:\Program Files\7-Zip\"
.\7z a $($path + 'Airtable.zip') $($path + 'build\*')


# Update Lambda
aws lambda update-function-code `
    --function-name Airtable `
    --zip-file $("fileb://" + $path + "Airtable.zip") `
	| Select-String -Pattern '(FunctionName)|(LastModified)'
