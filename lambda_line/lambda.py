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
                    thumbnail_image_url='https://dl.airtable.com/.attachmentThumbnails/5ea2b91702fe89e0eeda03bad475f98b/83e77c45',
                    image_background_color="#FFFFFF",
                    title='回家作業 1：抱狐狸',
                    text='未完成',
                    default_action=URIAction(
                        label='uri1',
                        uri='https://www.youtube.com/watch?v=Y-JQ-RCyPpQ'
                    ),                        
                    actions=[
                        MessageAction(
                            label='完成',
                            text='我完成了 抱狐狸'
                        )
                    ]
                ),
                CarouselColumn(
                    thumbnail_image_url='https://dl.airtable.com/.attachmentThumbnails/41f6cfcd1e50175a83240f73338f3f2b/67df816e',
                    image_background_color="#000000",
                    title='回家作業 2: 狐狸家族',
                    text='已完成',
                    default_action=URIAction(
                        label='uri2',
                        uri='https://www.youtube.com/watch?v=Y-JQ-RCyPpQ'
                    ),
                    actions=[
                        MessageAction(
                            label='完成',
                            text='我完成了 狐狸家族'
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

    # except LineBotApiError as err: pass
    except LineBotApiError as err: raise

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