import json
from datetime import datetime, date
from boto3 import client as boto3_client
lambda_client = boto3_client('lambda', region_name="us-east-1")


class AIR_EVENT_TYPES():
    REMINDER = 'reminder'


class LINE_EVENT_TYPES():
    PUSH = 'push'


class LAMBDA():
    AIRTABLE = 'Airtable'
    LINE = 'Line'


class Scheduler():
    scheduledJobs = []

    @classmethod
    def add(cls, evalExp):
        def wrapper(func):
            if eval(evalExp): cls.scheduledJobs.append(func)
        return wrapper


def lambda_handler(requestEvent, context):
    print('Checking {} at {}...'.format('scheduled jobs', requestEvent['time']))

    res = [event() for event in Scheduler.scheduledJobs]

    print('Check complete at {}.'.format(str(datetime.now())))


@Scheduler.add('not date.today().day % 1')  # This execute everyday
def job_reminder():
    resPayload = invokeLambda(LAMBDA.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.REMINDER
    })

    remindedInd = []
    for target in resPayload[0]['Data']:
        invokeLambda(LAMBDA.LINE, {
            'eventType': LINE_EVENT_TYPES.PUSH,
            'lineUserId': target['lineUserId'],
            'pushMessage': target['messageContent']
        })        
        remindedInd.append(target['lineDisplayName'])

    print('Reminder sent to {}.'.format(', '.join(remindedInd)))


def invokeLambda(lambdaName, payload):
    res = lambda_client.invoke(
        FunctionName=lambdaName,
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    # `resPayload` is an array with result of all activated handlers.
    resPayload = json.loads(res['Payload'].read().decode("utf-8"))
    return resPayload
