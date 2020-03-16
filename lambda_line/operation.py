from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage, TemplateSendMessage, FlexSendMessage
from template import getTemplate
from text import messageText


def pushMessage(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.PUSH,
        'lineUserId': target['lineUserId'],
        'pushMessage': target['messageContent']
    }
    '''
    print('Pushing message: {}'.format(event['pushMessage']))

    lineChannel.push_message(
        event['lineUserId'],
        TextSendMessage(text=event['pushMessage'])
    )


def replyMessage(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': LINE_MESSAGE_TEXTS
        'replyContent': {}
    }
    '''
    message = messageText(event['replyMessage'], event.get('replyContent', {}))
    print('Replying message: {}'.format(message))

    # Reply token can be used only once -> The default reply will not take place (and a LineBotApiError will be raised) if the reply has been made in cmd process
    try:
        lineChannel.reply_message(
            event['lineReplyToken'],
            TextSendMessage(text=message)
        )
    except LineBotApiError: raise


# TODO: Modify alt_text, which will be seen by user in notification
def replyMessage_carousel(lineChannel, event):
    '''
    event {
        'eventType': LINE_EVENT_TYPES.REPLY_CAROUSEL,
        'lineReplyToken': event.reply_token,
        'replyTemplate': LINE_MESSAGE_TEMPLATES.HOMEWORK,
        'replyContent': [{}]
    }
    '''
    print('Replying carousel: {}'.format(event['replyTemplate']))

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
    print('Replying flex: {}'.format(event['replyTemplate']))

    print(getTemplate(event['replyTemplate'])(event['replyContent']))
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
    print('Getting profile: {}'.format(event['lineUserId']))
    profileObj = lineChannel.get_profile(event['lineUserId'])

    return {
        'Status': 'handle_getProfile: OK',
        'Data': {
            'displayName': profileObj.display_name,
            'pictureUrl': profileObj.picture_url
        }
    }
