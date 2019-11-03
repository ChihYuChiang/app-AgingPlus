import os
from datetime import datetime
from boto3 import client as boto3_client
lambda_client = boto3_client('lambda', region_name="us-east-1")

class AIR_EVENT_TYPES():
    REMINDER = 'reminder'

class NoEventExcept(Exception):
    def __init__(self):
        self.message = 'No scheduled event to invoke.'

def lambda_handler(requestEvent, context):
    print('Checking {} at {}...'.format('scheduled jobs', requestEvent['time']))
    try:
        targetEvents = getTargetEvents()
        if not len(targetEvents): raise NoEventExcept()

        res = [invokeAirtable(event) for event in targetEvents]
    except NoEventExcept as exception: print(exception.message)
    except: raise
    else:
        print('Invoked {} events with responses:'.format(len(targetEvents)))
        print(res)
    finally:
        print('Check complete at {}.'.format(str(datetime.now())))


def getTargetEvents():
    '''
    Return the [events] to trigger.
    - Every day 1900 an Airtable reminder event.
    '''
    targetEvents = [
        {'eventType': AIR_EVENT_TYPES.REMINDER}
    ]
    return targetEvents

def invokeAirtable(payload):
    res = lambda_client.invoke(
        FunctionName="Airtable",
        InvocationType='RequestResponse',
        Payload=json.dumps(payload)
    )

    #`resPayload` is an array with result of all activated air handlers.
    resPayload = json.loads(res['Payload'].read().decode("utf-8"))
    return resPayload