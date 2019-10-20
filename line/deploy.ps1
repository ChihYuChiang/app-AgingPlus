Copy-Item "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\line\lambda.py" `
	-Destination "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\line\build"

Compress-Archive -Path "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\line\build\*" `
	-destinationpath "C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\line\Line.zip" `
	-compressionlevel optimal -Force

aws lambda update-function-code `
    --function-name Line `
    --zip-file "fileb://C:\Users\chihy\OneDrive\Ongoing - OneDrive\app-AgingPlus\line\Line.zip" `
	| Select-String -Pattern '(FunctionName)|(LastModified)'