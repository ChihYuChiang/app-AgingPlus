from __future__ import print_function
import boto3
import botocore.exceptions
import hmac
import hashlib
import base64
import json
import uuid
import logging
 
logger = logging.getLogger()
logger.setLevel(logging.INFO)

client = None

def get_secret_hash(username):
    msg = username + CLIENT_ID
    dig = hmac.new(str(CLIENT_SECRET).encode('utf-8'), 
        msg = str(msg).encode('utf-8'), digestmod=hashlib.sha256).digest()
    d2 = base64.b64encode(dig).decode()
    return d2

ERROR = 0
SUCCESS = 1
USER_EXISTS = 2
    
def sign_up(username, password):
    try:
        resp = client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=get_secret_hash(username),
            Username=username,
            Password=password)
        print(resp)
    except client.exceptions.UsernameExistsException as e:
        return USER_EXISTS
    except Exception as e:
        print(e)
        return ERROR
    return SUCCESS
    
def initiate_auth(username, password):
    try:
      # AdminInitiateAuth
        resp = client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'SECRET_HASH': get_secret_hash(username),
                'PASSWORD': password
            },
            ClientMetadata={
                'username': username,
                'password': password
            })
    except client.exceptions.NotAuthorizedException as e:
        return None, "Unauthorized"
    except client.exceptions.UserNotFoundException as e:
        return None, "Unauthorized"
    except Exception as e:
        # print(e)
        logger.error(e)
        return None, "Unknown error"
    return resp, None

def lambda_handler(event, context):
    global client
    if client == None:
        client = boto3.client('cognito-idp')

    # print(event)
    body = event
    username = body['username']
    password = body['password']
    
    resp, msg = initiate_auth(username, password)
    if msg != None:
        # return {'status': 'fail', 'message': msg}
        logger.info('failed signIN with username={}'.format(username))
        raise Exception(msg)

    logger.info('successful signIN with username={}'.format(username))
    id_token = resp['AuthenticationResult']['IdToken']
    access_token = resp['AuthenticationResult']['AccessToken']
    expires_in = resp['AuthenticationResult']['ExpiresIn']
    refresh_token = resp['AuthenticationResult']['RefreshToken']
    return {'status': 'success', 'id_token': id_token, 'access_token': access_token, 'expires_in': expires_in, 'refresh_token': refresh_token}