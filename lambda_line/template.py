from typing import List, Dict
from linebot.models import PostbackAction, MessageAction, URIAction
from linebot.models import CarouselTemplate, CarouselColumn


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
    HOMEWORK = 'homework'
    CLASS_HISTORY = 'class_history'
    CLASS_RECORD = 'class_record'


def carousel_homework(content: List[Dict]) -> Dict:
    '''
    content [{
        hwIid: 'rec123456',
        hwDate: '2020-03-01',
        noOfSet: 3,
        personalTip: '越像蟲越好',
        image: 'https://dl.airtable.com/.attachmentThumbnails/2e4132d7206ae8edddc79c6fd9525e78/62d6d3c6',
        video: 'https://www.youtube.com/watch?v=t_qk5ZhRHIs',
        isFinished: false,
        member: 'Bingo',
        baseMove: '滾筒按摩'
    }, {...}]
    '''
    def genItem(i, itemContent):
        colContent = {
            'thumbnail_image_url': itemContent['image'],
            'title': '回家作業 {}：{}'.format(i, itemContent['baseMove']),
            'text': '{} 組'.format(itemContent['noOfSet']),
            'default_action': userAction(LINE_USERACTION_TYPES.URI)(
                label='影片',
                uri=itemContent['video']
            ),
            'actions': [userAction(LINE_USERACTION_TYPES.POSTBACK)(
                label='已完成 ❤️',
                data='action=empty'
            )] if itemContent['isFinished'] else [userAction(LINE_USERACTION_TYPES.POSTBACK)(
                label='完成',
                display_text='我完成了 {}'.format(itemContent['baseMove']),
                data='action=finish_homework;hwIid={}'.format(itemContent['hwIid'])
            )]
        }
        return CarouselColumn(**colContent)

    return CarouselTemplate(
        columns=[genItem(i, itemContent) for i, itemContent in enumerate(content, 1)]
    )


def flex_classHistory(content: List[Dict]) -> Dict:
    '''
    Flex with carousel format.
    content [{
        'classIid': 'recvQFMu2DOSqwuBm', 'classTime': '1226', 'classLocation': '學員家', 'classDate': '0900', 'classTrainer': 'James'
    }, {...}]
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
                    "text": itemContent['classDate'],
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
                    "text": itemContent['classTime'],
                    "size": "sm",
                    "align": "start",
                    "color": "#8C8C8C"
                }, {
                    "type": "text",
                    "text": itemContent.get('classLocation', '上課場地'),
                    "size": "sm",
                    "wrap": True,
                    "color": "#8C8C8C"
                }, {
                    "type": "text",
                    "text": itemContent.get('classTrainer', '樂齡教練'),
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
                "displayText": "{} 課程內容".format(itemContent['classDate'])
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
    '''
    Flex with carousel format.
    content [{

    }, {...}]
    '''
    def genItem(i, itemContent):
        return {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "image",
                        "url": "https://scdn.line-apps.com/n/channel_devcenter/img/flexsnapshot/clip/clip1.jpg",
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
                                "text": "死蟲 Dead Worm",
                                "size": "lg",
                                "color": "#ffffff",
                                "weight": "bold"
                            }]
                        }, {
                            "type": "box",
                            "layout": "vertical",
                            "contents": [{
                                "type": "text",
                                "text": "10 組",
                                "color": "#ebebeb",
                                "size": "sm",
                                "flex": 0
                            }, {
                                "type": "text",
                                "text": "This is some word to be told to the client",
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
                            "text": "10",
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
                "uri": itemContent['video'],
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
