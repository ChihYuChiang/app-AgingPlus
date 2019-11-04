import os
import sys
import json

from linebot import LineBotApi
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import TextSendMessage
#https://github.com/line/line-bot-sdk-python
#https://developers.line.biz/en/reference/messaging-api/

#Get channel_access_token from your environment variable
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
class LINE_EVENT_TYPES():
    PUSH = 'push'
    REPLY = 'reply'
    GET_PROFILE = 'get_profile'


//TODO: make it middleware form
def lambda_handler(requestEvent, context):
    res = ''
    if requestEvent['eventType'] == LINE_EVENT_TYPES.REPLY:
        replyMessage(requestEvent)
    if requestEvent['eventType'] == LINE_EVENT_TYPES.PUSH:
        pushMessage(requestEvent)
    if requestEvent['eventType'] == LINE_EVENT_TYPES.GET_PROFILE:
        res = getProfile(requestEvent)

    return res


def pushMessage(event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.PUSH,
        'lineUserId': target['lineUserId'],
        'pushMessage': target['messageContent']
    }
    '''
    line_bot_api.push_message(
        event['lineUserId'],
        TextSendMessage(text=event['pushMessage'])
    )

def replyMessage(event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': replyMessage
    }
    '''
    #Reply token can be used only once -> The default reply will not take place (and a LineBotApiError will be raised) if the reply has been made in cmd process
    try:
        line_bot_api.reply_message(
            event['lineReplyToken'],
            TextSendMessage(text=event['replyMessage'])
        )
    except LineBotApiError as err: pass

def getProfile(event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.GET_PROFILE,
        'lineUserId': event.source.user_id
    }
    '''
    profileObj = line_bot_api.get_profile(event['lineUserId'])

    return {
        'Status': 'handle_getProfile: OK',
        'Data': {
            'displayName': profileObj.display_name,
            'pictureUrl': profileObj.picture_url
        }
    }