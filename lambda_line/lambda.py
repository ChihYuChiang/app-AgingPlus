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


//TODO: make it middleware form
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
        'replyMessage': https://developers.line.biz/en/reference/messaging-api/#carousel
    }
    '''
    try:
        carouselContent = CarouselTemplate(
            columns=[
                CarouselColumn(
                    thumbnail_image_url='https://via.placeholder.com/150',
                    imageBackgroundColor="#FFFFFF",
                    title='this is menu1',
                    text='description1',
                    defaultAction=URIAction(
                        label='uri1',
                        uri='http://youtube.com'
                    ),                        
                    actions=[
                        MessageAction(
                            label='完成',
                            text='我完成了項目1'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://example.com/item2.jpg',
                    imageBackgroundColor="#000000",
                    title='this is menu2',
                    text='description2',
                    defaultAction=URIAction(
                        label='uri2',
                        uri='http://youtube.com'
                    ),
                    actions=[
                        MessageAction(
                            label='message2',
                            text='我完成了項目2'
                        )
                    ]
                )
            ]
        )
    
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