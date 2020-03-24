import re
from util import invokeLambda
from util import POSTBACK_TYPES, AIR_EVENT_TYPES, LINE_EVENT_TYPES, LAMBDAS
from util import LINE_MESSAGE_TEMPLATES, LINE_MESSAGE_TEXTS


# TODO: Remove the list structure
# (User) Reply next class info
def cmd_nextClass(event):
    '''
    Success response =
    [{'Status': 'handle_nextClass: OK', 'Data': {'memberIid': 'recMgb6f5sfuhVWAs', 'classId': '1900322', 'classTime': '1114 09:00', 'classLocation': 'home', 'classTrainer': 'CY'}}]
    '''
    # Get next class info
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.NEXT_CLASS,
        'lineUserId': event.source.user_id
    })
    resData = resPayload and resPayload[0]['Data']

    # Reply to the message
    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        **({
            'replyMessage': LINE_MESSAGE_TEXTS.NEXT_CLASS_RECORD,
            'replyContent': resData
        } if resData else {
            'replyMessage': LINE_MESSAGE_TEXTS.NEXT_CLASS_NO_RECORD
        })
    })


# (User) Reply homework info
def cmd_homework(event):
    '''
    Success response =
    [{'Status': 'handle_homework: OK', 'Data': [{
        hwIid: 'rec123456',
        noOfSet: 3,
        personalTip: '越像蟲越好',
        image: 'https://dl.airtable.com/.attachmentThumbnails/2e4132d7206ae8edddc79c6fd9525e78/62d6d3c6',
        video: 'https://www.youtube.com/watch?v=t_qk5ZhRHIs',
        isFinished: false,
        member: 'Bingo',
        baseMove: '滾筒按摩'
    }]}]
    '''
    # Get homework info
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.HOMEWORK,
        'lineUserId': event.source.user_id
    })
    resData = resPayload and resPayload[0]['Data']

    # Reply to the request
    invokeLambda(LAMBDAS.LINE, {
        'lineReplyToken': event.reply_token,
        **({
            'eventType': LINE_EVENT_TYPES.REPLY_CAROUSEL,
            'replyTemplate': LINE_MESSAGE_TEMPLATES.HOMEWORK,
            'replyContent': resData
        } if resData else {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'replyMessage': LINE_MESSAGE_TEXTS.HOMEWORK_NO_RECORD
        })
    })


# (User) Update homework info
def btn_finishHomework(event):
    invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.FINISH_HOMEWORK,
        'hwIid': re.search('hwIid=(.+?)(;|$)', event.postback.data)[1]
    })


# (User) Reply class history
def cmd_classHistory(event):
    '''
    Success response =
    [{'Status': 'handle_classHistory: OK', 'Data': [{
        'classIid': 'recvQFMu2DOSqwuBm', 'classTime': '1226', 'classLocation': '學員家', 'classDate': '0900', 'classTrainer': 'James'}, {
        'classIid': 'recNO0A5FQCxMopYZ', 'classTime': '0927', 'classLocation': '學員主要戶外場地', 'classDate': '0930', 'classTrainer': 'James'
    }]}]
    '''
    # Get class history
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.CLASS_HISTORY,
        'lineUserId': event.source.user_id
    })
    resData = resPayload and resPayload[0]['Data']

    # Reply to the request
    invokeLambda(LAMBDAS.LINE, {
        'lineReplyToken': event.reply_token,
        **({
            'eventType': LINE_EVENT_TYPES.REPLY_FLEX,
            'replyTemplate': LINE_MESSAGE_TEMPLATES.CLASS_HISTORY,
            'replyContent': resData
        } if resData else {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'replyMessage': LINE_MESSAGE_TEXTS.CLASS_HISTORY_NO_RECORD
        })
    })


# (User) Get class detail records
def btn_classRecord(event):
    '''
    Success response =
    [{'Status': 'handle_classRecord: OK', 'Data': [{'baseMove': '橋式 Bridge'}, {'baseMove': '死蟲 Dead Bug'}, {'performanceRec': '四足跪姿；膝支撐平板夾背', 'image': 'https://dl.airtable.com/.attachmentThumbnails/2e4132d7206ae8edddc79c6fd9525e78/62d6d3c6', 'video': 'http://youtube.com', 'baseMove': '滾筒按摩'}]
    }]
    '''
    # Get class record
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.CLASS_RECORD,
        'classIid': re.search('classIid=(.+?)(;|$)', event.postback.data)[1]
    })
    resData = resPayload and resPayload[0]['Data']

    # Reply to the request
    invokeLambda(LAMBDAS.LINE, {
        'lineReplyToken': event.reply_token,
        **({
            'eventType': LINE_EVENT_TYPES.REPLY_FLEX,
            'replyTemplate': LINE_MESSAGE_TEMPLATES.CLASS_RECORD,
            'replyContent': resData
        } if resData else {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'replyMessage': LINE_MESSAGE_TEXTS.CLASS_RECORD_NO_RECORD
        })
    })


postbackHandlerMapping = {
    POSTBACK_TYPES.EMPTY: lambda x: None,
    POSTBACK_TYPES.NEXT_CLASS: cmd_nextClass,
    POSTBACK_TYPES.HOMEWORK: cmd_homework,
    POSTBACK_TYPES.CLASS_HISTORY: cmd_classHistory,
    POSTBACK_TYPES.CLASS_RECORD: btn_classRecord,
    POSTBACK_TYPES.FINISH_HOMEWORK: btn_finishHomework
}
