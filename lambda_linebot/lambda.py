import os
import sys
import json
import re
from typing import Dict, Optional
from boto3 import client as boto3_client
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, PostbackEvent
from util import EVENT_TYPES, AIR_EVENT_TYPES, LINE_EVENT_TYPES, LAMBDAS
from util import LINE_MESSAGE_TEMPLATES, LINE_MESSAGE_TEXTS
# https://github.com/line/line-bot-sdk-python
# https://developers.line.biz/en/reference/messaging-api/


# -- Setup
# TODO: encrypt keys on AWS
# TODO: mypy when matured
# TODO: pytest with testing db
# TODO: lambda layer to share enum and others
lambda_client = boto3_client('lambda', region_name="us-east-1")

# Get channel_secret from environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

# Line webhook
line_handler = WebhookHandler(channel_secret)


# TODO: apply Template pattern
# Trigger other lambdas (lambda_line, lambda_airtable)
def invokeLambda(lambdaName, payload):
    print('Invoke lambda: {}'.format(lambdaName))
    res = lambda_client.invoke(
        FunctionName=lambdaName,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    # `resPayload` is an array with result of all activated handlers.
    resPayload = json.loads(res['Payload'].read().decode("utf-8"))
    return resPayload


# -- Main handler
def lambda_handler(requestEvent, context):
    # Get X-Line-Signature header value
    signature = requestEvent['headers']['X-Line-Signature']

    # Get request body as text
    body = requestEvent['body']

    # Check the body-signature match and handle the event
    try: line_handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        raise

    return {'statusCode': 200, 'body': 'OK'}


# -- Handle PostbackEzvent type
# TODO: make it middleware form
@line_handler.add(PostbackEvent)
def handle_postback(event):
    eventAction = re.search('action=(.+?)(;|$)', event.postback.data)[1]
    print('Handle postback event: {}.'.format(eventAction))

    handlerMapping = {
        EVENT_TYPES.EMPTY: lambda x: None,
        EVENT_TYPES.NEXT_CLASS: cmd_nextClass,
        EVENT_TYPES.HOMEWORK: cmd_homework,
        EVENT_TYPES.CLASS_HISTORY: cmd_classHistory,
        EVENT_TYPES.CLASS_RECORD: btn_classRecord,
        EVENT_TYPES.FINISH_HOMEWORK: btn_finishHomework
    }
    handlerMapping[eventAction](event)


# (User) Reply next class info
def cmd_nextClass(event):
    '''
    Success response =
    [{'Status': 'handle_nextClass: OK', 'Data': {'memberIid': 'recMgb6f5sfuhVWAs', 'classId': '1900322', 'classTime': '1114 09:00', 'classLocation': 'home', 'classTrainer': 'CY'}}]
    '''
    # Get next class info
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.NEXT_CLASS,
        'lineUserId': event.source.user_id
    })
    resData: Optional[Dict] = resPayload and resPayload[0]['Data']

    # Reply to the message
    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        **({
            'replyMessage': LINE_MESSAGE_TEXTS.NEXT_CLASS_RECORD,
            'replyContent': resData
        } if resData else {
            'replyMessage': LINE_MESSAGE_TEXTS.NEXT_CLASS_NO_RECORD
        })
    })


# (User) Reply homework info
def cmd_homework(event):
    '''
    Success response =
    [{'Status': 'handle_homework: OK', 'Data': [{
        hwIid: 'rec123456',
        noOfSet: 3,
        personalTip: '越像蟲越好',
        image: 'https://dl.airtable.com/.attachmentThumbnails/2e4132d7206ae8edddc79c6fd9525e78/62d6d3c6',
        video: 'https://www.youtube.com/watch?v=t_qk5ZhRHIs',
        isFinished: false,
        member: 'Bingo',
        baseMove: '滾筒按摩'
    }]}]
    '''
    # Get homework info
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.HOMEWORK,
        'lineUserId': event.source.user_id
    })
    resData: Optional[Dict] = resPayload and resPayload[0]['Data']

    # Reply to the request
    invokeLambda(LAMBDAS.LINE, {
        'lineReplyToken': event.reply_token,
        **({
            'eventType': LINE_EVENT_TYPES.REPLY_CAROUSEL,
            'replyTemplate': LINE_MESSAGE_TEMPLATES.HOMEWORK,
            'replyContent': resData
        } if resData else {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'replyMessage': LINE_MESSAGE_TEXTS.HOMEWORK_NO_RECORD
        })
    })


# (User) Update homework info
def btn_finishHomework(event):
    invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.FINISH_HOMEWORK,
        'hwIid': re.search('hwIid=(.+?)(;|$)', event.postback.data)[1]
    })


# (User) Reply class history
def cmd_classHistory(event):
    '''
    Success response =
    [{'Status': 'handle_classHistory: OK', 'Data': [{
        'classIid': 'recvQFMu2DOSqwuBm', 'classTime': '1226', 'classLocation': '學員家', 'classDate': '0900', 'classTrainer': 'James'}, {
        'classIid': 'recNO0A5FQCxMopYZ', 'classTime': '0927', 'classLocation': '學員主要戶外場地', 'classDate': '0930', 'classTrainer': 'James'
    }]}]
    '''
    # Get class history
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.CLASS_HISTORY,
        'lineUserId': event.source.user_id
    })
    resData: Optional[Dict] = resPayload and resPayload[0]['Data']

    # Reply to the request
    invokeLambda(LAMBDAS.LINE, {
        'lineReplyToken': event.reply_token,
        **({
            'eventType': LINE_EVENT_TYPES.REPLY_FLEX,
            'replyTemplate': LINE_MESSAGE_TEMPLATES.CLASS_HISTORY,
            'replyContent': resData
        } if resData else {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'replyMessage': LINE_MESSAGE_TEXTS.CLASS_HISTORY_NO_RECORD
        })
    })


# (User) Get class detail records
def btn_classRecord(event):
    '''
    Success response =
    [{'Status': 'handle_classRecord: OK', 'Data': [{'baseMove': '橋式 Bridge'}, {'baseMove': '死蟲 Dead Bug'}, {'performanceRec': '四足跪姿；膝支撐平板夾背', 'image': 'https://dl.airtable.com/.attachmentThumbnails/2e4132d7206ae8edddc79c6fd9525e78/62d6d3c6', 'video': 'http://youtube.com', 'baseMove': '滾筒按摩'}]
    }]
    '''
    # Get class record
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.CLASS_RECORD,
        'classIid': re.search('classIid=(.+?)(;|$)', event.postback.data)[1]
    })
    resData: Optional[Dict] = resPayload and resPayload[0]['Data']

    # Reply to the request
    invokeLambda(LAMBDAS.LINE, {
        'lineReplyToken': event.reply_token,
        **({
            'eventType': LINE_EVENT_TYPES.REPLY_FLEX,
            'replyTemplate': LINE_MESSAGE_TEMPLATES.CLASS_RECORD,
            'replyContent': resData
        } if resData else {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'replyMessage': LINE_MESSAGE_TEXTS.CLASS_RECORD_NO_RECORD
        })
    })


# -- Handle MessageEvent and TextMessage type
@line_handler.add(MessageEvent, TextMessage)
def handle_message(event):
    # TODO: Better admin command model
    if event.message.text == 'r': adm_reminder(event)

    # TODO: Switch to log module
    print(json.dumps({
        'logType': 'MessageEvent',
        'lineUserId': event.source.user_id,
        'msgContent': event.message.text
    }))

    # Default reply replicates the incoming message
    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': event.message.text
    })


# 'r' -> (Admin) Send reminder of upcoming classes
# TODO: Deal with no one to send reminder
# TODO: Get everyday log of all message sent to the bot: AWS CLI into csv, time, identity, message
def adm_reminder(event):
    '''
    Success response =
    [{'Status': 'handle_reminder: OK', 'Data': [{'iid': 'recGPvFMiUDaoO4', 'lineUserId': 'U9ae6458c650504a3e8380a1046e0f', 'lineDisplayName': 'CY', 'messageTime': '2019-10-28T13:13:00.000Z', 'messageContent': "Hello, this is a response from air."}]}]
    '''
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.REMINDER
    })

    remindedInd = []
    for target in (resPayload and resPayload[0]['Data']):
        invokeLambda(LAMBDAS.LINE, {
            'eventType': LINE_EVENT_TYPES.PUSH,
            'lineUserId': target['lineUserId'],
            'pushMessage': target['messageContent']
        })
        remindedInd.append(target['lineDisplayName'])

    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': LINE_MESSAGE_TEXTS.REMINDER_SUCCESS,
        'replyContent': {
            'remindedInds': ', '.join(remindedInd)
        }
    })


# -- Handle FollowEvent (when someone adds this account as friend)
@line_handler.add(FollowEvent)
def handle_follow(event):
    print('Handle follow event: {}.'.format(event.source.user_id))
    resPayload = invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.GET_PROFILE,
        'lineUserId': event.source.user_id
    })
    userDisplayName = resPayload['Data']['displayName']
    userProfilePic = resPayload['Data']['pictureUrl']

    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': LINE_MESSAGE_TEXTS.FOLLOW_GREETING,
        'replyContent': {
            'userName': userDisplayName
        }
    })

    invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.FOLLOW,
        'lineUserId': event.source.user_id,
        'lineDisplayName': userDisplayName,
        'lineProfilePic': userProfilePic
    })
