import os
import sys
import json
from boto3 import client as boto3_client
lambda_client = boto3_client('lambda', region_name="us-east-1")

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, TextSendMessage
#https://github.com/line/line-bot-sdk-python
#https://developers.line.biz/en/reference/messaging-api/
#TODO: encrypt keys on AWS

#Get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
line_handler = WebhookHandler(channel_secret)
class AIR_EVENT_TYPES():
    FOLLOW = 'follow'
    REMINDER = 'reminder'


def lambda_handler(requestEvent, context):
    #Get X-Line-Signature header value
    signature = requestEvent['headers']['X-Line-Signature']    
    
    #Get request body as text    
    body = requestEvent['body']

    #Check the body-signature match and handle the event
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return {'statusCode': 200, 'body': 'OK'}


#--Handle MessageEvent and TextMessage type
#General response
@line_handler.add(MessageEvent, TextMessage)
def handle_message(event):
    if event.message.text == 'r': cmd_reminder()

    response = event.message.text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

#'r' -> Reminder of upcoming class
def cmd_reminder():
    '''
    Success response = 
    [{'Status': 'handle_reminder: OK', 'Data': [{'id': 'recGPvFMiUDaoO4', 'lineUserId': 'U9ae6458c650504a3e8380a1046e0f', 'lineDisplayName': 'CY', 'messageTime': '2019-10-28T13:13:00.000Z', 'messageContent': "Hello, this is a response from air."}]}]
    '''
    resPayload = invokeAirtable({
        'eventType': AIR_EVENT_TYPES.REMINDER
    })

    for target in resPayload[0]['Data']:
        line_bot_api.push_message(
            target['lineUserId'],
            TextSendMessage(text=target['messageContent'])
        )
        print('Sent msg to ', target['lineUserId'], '.')


#--Handle FollowEvent (when someone adds this account as friend)
@line_handler.add(FollowEvent)
def handle_follow(event):
    userProfile = line_bot_api.get_profile(event.source.user_id)

    response = 'Hello, ' + userProfile.display_name
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

    invokeAirtable({
        'eventType': AIR_EVENT_TYPES.FOLLOW,
        'lineUserId': event.source.user_id,
        'lineDisplayName': userProfile.display_name
    })


def invokeAirtable(payload):
    res = lambda_client.invoke(
        FunctionName="Airtable",
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    #`resPayload` is an array with result of all activated air handlers.
    resPayload = json.loads(res['Payload'].read().decode("utf-8"))
    return resPayload