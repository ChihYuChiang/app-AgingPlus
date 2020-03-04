import os
import sys
import json

from linebot import LineBotApi
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import TextSendMessage, TemplateSendMessage
from linebot.models import CarouselTemplate, CarouselColumn
from linebot.models import PostbackAction, MessageAction, URIAction
# https://github.com/line/line-bot-sdk-python
# https://developers.line.biz/en/reference/messaging-api/

# Get channel_access_token from your environment variable
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
class LINE_EVENT_TYPES():
    PUSH = 'push'
    REPLY = 'reply'
    REPLY_CAROUSEL = 'reply_carousel'
    GET_PROFILE = 'get_profile'

class LINE_USERACTION_TYPES():
    POSTBACK = 'post_back'
    MESSAGE = 'message'
    URI = 'uri'
def userAction(userActionType):
    return {
        LINE_USERACTION_TYPES.POSTBACK: PostbackAction,
        LINE_USERACTION_TYPES.MESSAGE: MessageAction,
        LINE_USERACTION_TYPES.URI: URIAction
    }[userActionType]


#-- Main handler
# TODO: make it middleware form
def lambda_handler(requestEvent, context):
    res = ''
    eventType = requestEvent['eventType']
    if eventType == LINE_EVENT_TYPES.REPLY:
        replyMessage(requestEvent)
    elif eventType == LINE_EVENT_TYPES.REPLY_CAROUSEL:
        replyMessage_carousel(requestEvent)
    elif eventType == LINE_EVENT_TYPES.PUSH:
        pushMessage(requestEvent)
    elif eventType == LINE_EVENT_TYPES.GET_PROFILE:
        res = getProfile(requestEvent)

    return res


#-- Operations
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
        'replyMessage': str
    }
    '''
    # Reply token can be used only once -> The default reply will not take place (and a LineBotApiError will be raised) if the reply has been made in cmd process
    try:
        line_bot_api.reply_message(
            event['lineReplyToken'],
            TextSendMessage(text=event['replyMessage'])
        )
    except LineBotApiError as err: pass

def replyMessage_carousel(event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.REPLY_CAROUSEL,
        'lineReplyToken': event.reply_token,
        'replyMessage': [{
            'main': {
                'thumbnail_image_url': 'https://dl.airtable.com/.attachmentThumbnails/',
                'title': '回家作業 1：抱狐狸',
                'text': '未完成'
            },
            'defaultAction': {
                'type': LINE_USERACTION_TYPES,
                'content': {
                    'label': '完成',
                    'uri'/'text'/'display_text': '我完成了 抱狐狸',
                    ('data': 'action=homework;happy=yes') -- Needed when postback
                }
            },
            'actions': [{
                'type': LINE_USERACTION_TYPES,
                'content': {}
            }, {...}]
        }, {...}]
    }
    '''
    # Parse string into dict
    replyMessage = json.loads(event['replyMessage'])

    # Construct columns
    def makeColumn(colContent):
        return CarouselColumn(
            **colContent['main'],
            default_action=userAction(colContent['defaultAction']['type'])(**colContent['defaultAction']['content']),
            actions=[userAction(action['type'])(**action['content']) for action in colContent['actions']]
        )
    carouselContent = CarouselTemplate(
        columns=[makeColumn(colContent) for colContent in replyMessage]
    )
        
    try:
        line_bot_api.reply_message(
            event['lineReplyToken'],
            TemplateSendMessage(
                alt_text='Carousel template',
                template=carouselContent
            )
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