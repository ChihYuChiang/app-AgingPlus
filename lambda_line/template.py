import json
from typing import List, Dict
from linebot.models import PostbackAction, MessageAction, URIAction


# -- User action
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


# -- Templates
class LINE_MESSAGE_TEMPLATES():
    CLASS_HISTORY = 'class_history'


def temp_classHistory(content: List[Dict]) -> Dict:
    '''
    Flex with carousel format.
    '''
    def genItem(i, itemContent):
        return {
            "type": "bubble",
            "size": "nano",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": itemContent['date'],
                    "color": "#ffffff",
                    "align": "start",
                    "size": "md",
                    "gravity": "center"
                }],
                "backgroundColor": "#27ACB2",
                "paddingTop": "19px",
                "paddingAll": "12px",
                "paddingBottom": "16px"
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": itemContent['time'],
                    "size": "sm",
                    "align": "start",
                    "color": "#8C8C8C"
                }, {
                    "type": "text",
                    "text": itemContent['location'],
                    "size": "sm",
                    "wrap": True,
                    "color": "#8C8C8C"
                }, {
                    "type": "text",
                    "text": itemContent['trainer'],
                    "size": "sm",
                    "color": "#8C8C8C"
                }],
                "spacing": "md",
                "paddingAll": "12px"
            },
            "action": {
                "type": LINE_USERACTION_TYPES.POSTBACK,
                "label": "action",
                "data": 'action=class_record;classIid={}'.format(itemContent['classIid']),
                "displayText": "{} 課程內容".format(itemContent['date'])
            },
            "styles": {
                "footer": {
                    "separator": False
                }
            }
        }

    return {
        "type": "carousel",
        "contents": [genItem(i, itemContent) for i, itemContent in enumerate(content, 1)]
    }


def getTemplate(template):
    return {
        LINE_MESSAGE_TEMPLATES.CLASS_HISTORY: temp_classHistory
    }[template]
