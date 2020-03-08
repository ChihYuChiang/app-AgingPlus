import os
import sys
from linebot import LineBotApi
from operation import pushMessage, getProfile
from operation import replyMessage, replyMessage_carousel, replyMessage_flex
# https://github.com/line/line-bot-sdk-python
# https://developers.line.biz/en/reference/messaging-api/


# -- Setup
# Get channel_access_token from your environment variable
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

lineChannel = LineBotApi(channel_access_token)


class LINE_EVENT_TYPES():
    PUSH = 'push'
    REPLY = 'reply'
    REPLY_CAROUSEL = 'reply_carousel'
    REPLY_FLEX = 'reply_flex'
    GET_PROFILE = 'get_profile'


def handleLineEvent(event):
    return {
        LINE_EVENT_TYPES.PUSH: pushMessage,
        LINE_EVENT_TYPES.REPLY: replyMessage,
        LINE_EVENT_TYPES.REPLY_CAROUSEL: replyMessage_carousel,
        LINE_EVENT_TYPES.REPLY_FLEX: replyMessage_flex,
        LINE_EVENT_TYPES.GET_PROFILE: getProfile
    }[event['eventType']](lineChannel, event)


# -- Main handler
# TODO: make it middleware form
def lambda_handler(requestEvent, context):
    return handleLineEvent(requestEvent)
