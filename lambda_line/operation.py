from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage, TemplateSendMessage, FlexSendMessage
from template import getTemplate


def pushMessage(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.PUSH,
        'lineUserId': target['lineUserId'],
        'pushMessage': target['messageContent']
    }
    '''
    lineChannel.push_message(
        event['lineUserId'],
        TextSendMessage(text=event['pushMessage'])
    )


# TODO: Combine reply functions
def replyMessage(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': str
    }
    '''
    # Reply token can be used only once -> The default reply will not take place (and a LineBotApiError will be raised) if the reply has been made in cmd process
    try:
        lineChannel.reply_message(
            event['lineReplyToken'],
            TextSendMessage(text=event['replyMessage'])
        )
    except LineBotApiError: raise


def replyMessage_carousel(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.REPLY_CAROUSEL,
        'lineReplyToken': event.reply_token,
        'replyTemplate': LINE_MESSAGE_TEMPLATES.HOMEWORK,
        'replyContent': [{}]
    }
    '''
    try:
        lineChannel.reply_message(
            event['lineReplyToken'],
            TemplateSendMessage(
                alt_text='Carousel template',
                template=getTemplate(event['replyTemplate'])(event['replyContent'])
            )
        )
    except LineBotApiError: raise


def replyMessage_flex(lineChannel, event):
    '''
    Flex Message Simulator -> get json -> make dict -> use as content
    https://developers.line.biz/console/fx/
    '''
    try:
        lineChannel.reply_message(
            event['lineReplyToken'],
            FlexSendMessage(
                alt_text='flex',
                contents=getTemplate(event['replyTemplate'])(event['replyContent'])
            )
        )
    except LineBotApiError: raise


def getProfile(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.GET_PROFILE,
        'lineUserId': event.source.user_id
    }
    '''
    profileObj = lineChannel.get_profile(event['lineUserId'])

    return {
        'Status': 'handle_getProfile: OK',
        'Data': {
            'displayName': profileObj.display_name,
            'pictureUrl': profileObj.picture_url
        }
    }
