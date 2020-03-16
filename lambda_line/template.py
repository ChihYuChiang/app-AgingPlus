from collections import ChainMap
from typing import List, Dict
from linebot.models import PostbackAction, MessageAction, URIAction
from linebot.models import CarouselTemplate, CarouselColumn


# -- User action
class LINE_USERACTION_TYPES():
    POSTBACK = 'postback'
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
    HOMEWORK = 'homework'
    CLASS_HISTORY = 'class_history'
    CLASS_RECORD = 'class_record'


def carousel_homework(content: List[Dict]) -> Dict:
    default = {  # `None` marks the attribute as required
        'hwIid': None,
        'member': None,
        'noOfSet': 3,
        'personalTip': '',
        # TODO: Provide default image and video
        'image': 'https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip1.jpg',
        'video': 'https://www.youtube.com',
        'isFinished': False,
        'baseMove': '基本動作'
    }

    def genItem(i, itemContent):
        itemContentWD = ChainMap(itemContent, default)
        colContent = {
            'thumbnail_image_url': itemContentWD['image'],
            'title': '回家作業 {}：{}'.format(i, itemContentWD['baseMove']),
            'text': '{} 組'.format(itemContentWD['noOfSet']),
            'default_action': userAction(LINE_USERACTION_TYPES.URI)(
                label='影片',
                uri=itemContentWD['video']
            ),
            'actions': [userAction(LINE_USERACTION_TYPES.POSTBACK)(
                label='已完成 ❤️',
                data='action=empty'
            )] if itemContentWD['isFinished'] else [userAction(LINE_USERACTION_TYPES.POSTBACK)(
                label='完成',
                display_text='我完成了 {}'.format(itemContentWD['baseMove']),
                data='action=finish_homework;hwIid={}'.format(itemContentWD['hwIid'])
            )]
        }
        return CarouselColumn(**colContent)

    return CarouselTemplate(
        columns=[genItem(i, itemContent) for i, itemContent in enumerate(content, 1)]
    )


def flex_classHistory(content: List[Dict]) -> Dict:
    default = {
        'classIid': None,
        'classDate': None,
        'classTime': None,
        'classLocation': '上課場地',
        'classTrainer': '樂齡教練',
    }

    def genItem(i, itemContent):
        itemContentWD = ChainMap(itemContent, default)
        return {
            "type": "bubble",
            "size": "nano",
            "header": {
                "type": "box",
                "layout": "vertical",
                "contents": [{
                    "type": "text",
                    "text": itemContentWD['classDate'],
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
                    "text": itemContentWD['classTime'],
                    "size": "sm",
                    "align": "start",
                    "color": "#8C8C8C"
                }, {
                    "type": "text",
                    "text": itemContentWD['classLocation'],
                    "size": "sm",
                    "wrap": True,
                    "color": "#8C8C8C"
                }, {
                    "type": "text",
                    "text": itemContentWD['classTrainer'],
                    "size": "sm",
                    "color": "#8C8C8C"
                }],
                "spacing": "md",
                "paddingAll": "12px"
            },
            "action": {
                "type": LINE_USERACTION_TYPES.POSTBACK,
                "label": "action",
                "data": 'action=class_record;classIid={}'.format(itemContentWD['classIid']),
                "displayText": "{} 課程內容".format(itemContentWD['classDate'])
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


def flex_classRecord(content: List[Dict]) -> Dict:
    default = {
        'baseMove': '基本動作',
        'performanceRec': '做得很好',
        # TODO: Provide default image and video
        'image': 'https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip1.jpg',
        'video': 'https://www.youtube.com'
    }

    def genItem(i, itemContent):
        itemContentWD = ChainMap(itemContent, default)
        return {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": itemContentWD.get['image'],
                        "size": "full",
                        "aspectMode": "cover",
                        "aspectRatio": "2:3",
                        "gravity": "top"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [{
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": itemContentWD['baseMove'],
                                "size": "lg",
                                "color": "#ffffff",
                                "weight": "bold"
                            }]
                        }, {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": "3 組",
                                "color": "#ebebeb",
                                "size": "sm",
                                "flex": 0
                            }, {
                                "type": "text",
                                "text": itemContentWD.get['performanceRec'],
                                "color": "#ffffffcc",
                                "flex": 0,
                                "size": "sm",
                                "wrap": True
                            }],
                            "spacing": "lg"
                        }],
                        "position": "absolute",
                        "offsetBottom": "0px",
                        "offsetStart": "0px",
                        "offsetEnd": "0px",
                        "backgroundColor": "#03303Acc",
                        "paddingAll": "20px",
                        "paddingTop": "18px",
                        "height": "150px"
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [{
                            "type": "text",
                            "text": str(i),
                            "color": "#ffffff",
                            "align": "center",
                            "size": "xs",
                            "offsetTop": "5px"
                        }],
                        "position": "absolute",
                        "cornerRadius": "20px",
                        "offsetTop": "18px",
                        "backgroundColor": "#ff334b",
                        "offsetStart": "18px",
                        "height": "30px",
                        "width": "30px"
                    }
                ],
                "paddingAll": "0px"
            },
            "action": {
                "type": LINE_USERACTION_TYPES.URI,
                "label": "影片",
                "uri": itemContentWD.get['video'],
            }
        }

    return {
        "type": "carousel",
        "contents": [genItem(i, itemContent) for i, itemContent in enumerate(content, 1)]
    }


def getTemplate(template):
    return {
        LINE_MESSAGE_TEMPLATES.CLASS_HISTORY: flex_classHistory,
        LINE_MESSAGE_TEMPLATES.CLASS_RECORD: flex_classRecord,
        LINE_MESSAGE_TEMPLATES.HOMEWORK: carousel_homework
    }[template]
