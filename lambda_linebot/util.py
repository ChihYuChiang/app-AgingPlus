import json
from Typing import Dict
from boto3 import client as boto3_client

lambda_client = boto3_client('lambda', region_name="us-east-1")


# Trigger other lambdas (lambda_line, lambda_airtable)
def invokeLambda(lambdaName: str, payload: Dict) -> Dict:
    print('Invoke lambda: {}'.format(lambdaName))
    res = lambda_client.invoke(
        FunctionName=lambdaName,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    # `resPayload` is an array with result of all activated handlers.
    resPayload = json.loads(res['Payload'].read().decode("utf-8"))
    return resPayload


class POSTBACK_TYPES():
    FOLLOW = 'follow'
    REMINDER = 'reminder'
    NEXT_CLASS = 'next_class'
    HOMEWORK = 'homework'
    FINISH_HOMEWORK = 'finish_homework'
    CLASS_HISTORY = 'class_history'
    CLASS_RECORD = 'class_record'
    EMPTY = 'empty'


class AIR_EVENT_TYPES():
    FOLLOW = 'follow'
    REMINDER = 'reminder'
    NEXT_CLASS = 'next_class'
    HOMEWORK = 'homework'
    FINISH_HOMEWORK = 'finish_homework'
    CLASS_HISTORY = 'class_history'
    CLASS_RECORD = 'class_record'


class LINE_EVENT_TYPES():
    PUSH = 'push'
    REPLY = 'reply'
    REPLY_CAROUSEL = 'reply_carousel'
    REPLY_FLEX = 'reply_flex'
    GET_PROFILE = 'get_profile'


class LAMBDAS():
    AIRTABLE = 'Airtable'
    LINE = 'Line'


class LINE_MESSAGE_TEMPLATES():
    HOMEWORK = 'homework'
    CLASS_HISTORY = 'class_history'
    CLASS_RECORD = 'class_record'


class LINE_MESSAGE_TEXTS():
    HOMEWORK_NO_RECORD = 'homework_no_record'
    CLASS_HISTORY_NO_RECORD = 'class_history_no_record'
    CLASS_RECORD_NO_RECORD = 'class_record_no_record'
    NEXT_CLASS_NO_RECORD = 'next_class_no_record'
    NEXT_CLASS_RECORD = 'next_class_record'
    FOLLOW_GREETING = 'follow_greeting'
    REMINDER_SUCCESS = 'reminder_success'
