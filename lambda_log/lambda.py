from boto3 import client as boto3_client
lambda_client = boto3_client('lambda', region_name="us-east-1")
