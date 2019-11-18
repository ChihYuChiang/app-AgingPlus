import os
import sys
import json
import re
from datetime import datetime
from boto3 import client as boto3_client
lambda_client = boto3_client('lambda', region_name="us-east-1")

from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, PostbackEvent
#https://github.com/line/line-bot-sdk-python
#https://developers.line.biz/en/reference/messaging-api/
#TODO: encrypt keys on AWS

#Get channel_secret from environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

line_handler = WebhookHandler(channel_secret)
class AIR_EVENT_TYPES():
    FOLLOW = 'follow'
    REMINDER = 'reminder'
    NEXT_CLASS = 'next_class'
class LINE_EVENT_TYPES():
    PUSH = 'push'
    REPLY = 'reply'
    GET_PROFILE = 'get_profile'
class LAMBDA():
    AIRTABLE = 'Airtable'
    LINE = 'Line'


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


#--Handle PostbackEvent type
@line_handler.add(PostbackEvent)
def handle_postback(event):
    eventAction = re.search('action=(.+);?', event.postback.data)[1]
    if eventAction == AIR_EVENT_TYPES.NEXT_CLASS: cmd_nextClass(event)

#(User) Reply next class info
def cmd_nextClass(event):
    '''
    Success response = 
    [{'Status': 'handle_nextClass: OK', 'Data': {'memberId': 'recMgb6f5sfuhVWAs', 'classId': '1900322', 'classTime': '2019-11-14T09:00:00+08:00', 'classLocation': 'home', 'classTrainer': 'CY'}}]
    '''    
    #Get next class info
    resPayload = invokeLambda(LAMBDA.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.NEXT_CLASS,
        'lineUserId': event.source.user_id
    })

    def genReply(data):
        if data: #If the res data is not null
            return 'Your next class is {} at {}. Your trainer is {} 😉.'.format(
                datetime.fromisoformat(data['classTime']).strftime('%m/%d %H:%M'),
                data['classLocation'],
                data['classTrainer']
            )
        else: return 'We don\'t have record of your next class 😢.'
    
    #Reply to the message
    invokeLambda(LAMBDA.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': genReply(resPayload[0]['Data'])
    })


#--Handle MessageEvent and TextMessage type
@line_handler.add(MessageEvent, TextMessage)
def handle_message(event):
    if event.message.text == 'r': cmd_reminder(event)

    #TODO: Switch to log module
    print(json.dumps({
        'logType': 'MessageEvent',
        'lineUserId': event.source.user_id,
        'msgContent': event.message.text
    }))

    #Default reply replicates the incoming message
    invokeLambda(LAMBDA.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': event.message.text
    })

#'r' -> (Admin) Send reminder of upcoming classes
#TODO: Check the admin identity
#TODO: Deal with no one to send reminder
#TODO: Admin group message and test
#TODO: Admin group message by group and indi message
#TODO: Get everyday log of all message sent to the bot: AWS CLI into csv, time, identity, message
def cmd_reminder(event):
    '''
    Success response = 
    [{'Status': 'handle_reminder: OK', 'Data': [{'id': 'recGPvFMiUDaoO4', 'lineUserId': 'U9ae6458c650504a3e8380a1046e0f', 'lineDisplayName': 'CY', 'messageTime': '2019-10-28T13:13:00.000Z', 'messageContent': "Hello, this is a response from air."}]}]
    '''
    resPayload = invokeLambda(LAMBDA.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.REMINDER
    })

    remindedInd = []
    for target in resPayload[0]['Data']:
        invokeLambda(LAMBDA.LINE, {
            'eventType': LINE_EVENT_TYPES.PUSH,
            'lineUserId': target['lineUserId'],
            'pushMessage': target['messageContent']
        })        
        remindedInd.append(target['lineDisplayName'])
    
    reply = 'Reminder sent to {}.'.format(', '.join(remindedInd))
    invokeLambda(LAMBDA.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': reply
    })


#--Handle FollowEvent (when someone adds this account as friend)
@line_handler.add(FollowEvent)
def handle_follow(event):
    resPayload = invokeLambda(LAMBDA.LINE, {
        'eventType': LINE_EVENT_TYPES.GET_PROFILE,
        'lineUserId': event.source.user_id
    })
    userDisplayName = resPayload['Data']['displayName']
    userProfilePic = resPayload['Data']['pictureUrl']

    reply = 'Hello, {} 😄.'.format(userDisplayName)
    invokeLambda(LAMBDA.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': reply
    })

    invokeLambda(LAMBDA.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.FOLLOW,
        'lineUserId': event.source.user_id,
        'lineDisplayName': userDisplayName,
        'lineProfilePic': userProfilePic
    })


def invokeLambda(lambdaName, payload):
    res = lambda_client.invoke(
        FunctionName=lambdaName,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    #`resPayload` is an array with result of all activated handlers.
    resPayload = json.loads(res['Payload'].read().decode("utf-8"))
    return resPayload