from util import Logger, LAMBDA_NAME
from util import invokeLambda
from util import AIR_EVENT_TYPES, LINE_EVENT_TYPES, LAMBDAS
from util import LINE_MESSAGE_TEXTS

# Logger
logger = Logger(LAMBDA_NAME)


# 'r' -> (Admin) Send reminder of upcoming classes
def adm_reminder(event):
    '''
    Success response =
    [{'Status': 'handle_reminder: OK', 'Data': [{'iid': 'recGPvFMiUDaoO4', 'lineUserId': 'U9ae6458c650504a3e8380a1046e0f', 'lineDisplayName': 'CY', 'messageTime': '2019-10-28T13:13:00.000Z', 'messageContent': "Hello, this is a response from air."}]}]
    '''
    # Get targets to send reminder
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.REMINDER
    })
    resData = resPayload and resPayload[0]['Data']
    logger.debug('Targets to send reminder: {}'.format(resData))

    # Send reminders to the targets
    if resData:
        remindedInd = []
        for target in resData:
            invokeLambda(LAMBDAS.LINE, {
                'eventType': LINE_EVENT_TYPES.PUSH,
                'lineUserId': target['lineUserId'],
                'pushMessage': target['messageContent']
            })
            remindedInd.append(target['lineDisplayName'])
    logger.debug('Pushed reminders to targets.')

    # Reply to the admin
    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        **({
            'replyMessage': LINE_MESSAGE_TEXTS.REMINDER_SUCCESS,
            'replyContent': {
                'remindedInds': ', '.join(remindedInd)
            }
        } if resData else {
            'replyMessage': LINE_MESSAGE_TEXTS.REMINDER_NO_TARGET
        })
    })
    logger.debug('Replied with sent reminder target ids.')


adminMsgHandlerMapping = {
    'r': adm_reminder
}
