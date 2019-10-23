import os
import sys

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
#https://github.com/line/line-bot-sdk-python
#https://developers.line.biz/en/reference/messaging-api/


# get channel_secret and channel_access_token from your environment variable
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


def parseEvent(event):
    profile = line_bot_api.get_profile(event.source.user_id)
    message = event.message

    return {'profile': profile, 'message': message}

def lambda_handler(requestEvent, context):
    #Get X-Line-Signature header value
    signature = requestEvent['headers']['X-Line-Signature']    
    
    #Get request body as text    
    body = requestEvent['body']
    print(body)

    #Check the body-signature match and handle the event
    try:
        line_handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return {'statusCode': 200, 'body': 'OK'}

#Handle MessageEvent and TextMessage type
@line_handler.add(MessageEvent, TextMessage)
def handle_message(event):
    parsedEvent = parseEvent(event)

    response = parsedEvent.text
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))

#Handle FollowEvent (when someone adds this account as friend)
@line_handler.add(FollowEvent)
def handle_message(event):
    parsedEvent = parseEvent(event)

    response = 'Hello, ' + parsedEvent['profile'].display_name
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=response))