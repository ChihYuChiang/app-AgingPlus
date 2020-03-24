from util import invokeLambda
from util import AIR_EVENT_TYPES, LINE_EVENT_TYPES, LAMBDAS
from util import LINE_MESSAGE_TEXTS


# 'r' -> (Admin) Send reminder of upcoming classes
# TODO: Deal with no one to send reminder
# TODO: Get everyday log of all message sent to the bot: AWS CLI into csv, time, identity, message
def adm_reminder(event):
    '''
    Success response =
    [{'Status': 'handle_reminder: OK', 'Data': [{'iid': 'recGPvFMiUDaoO4', 'lineUserId': 'U9ae6458c650504a3e8380a1046e0f', 'lineDisplayName': 'CY', 'messageTime': '2019-10-28T13:13:00.000Z', 'messageContent': "Hello, this is a response from air."}]}]
    '''
    resPayload = invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.REMINDER
    })

    remindedInd = []
    for target in (resPayload and resPayload[0]['Data']):
        invokeLambda(LAMBDAS.LINE, {
            'eventType': LINE_EVENT_TYPES.PUSH,
            'lineUserId': target['lineUserId'],
            'pushMessage': target['messageContent']
        })
        remindedInd.append(target['lineDisplayName'])

    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': LINE_MESSAGE_TEXTS.REMINDER_SUCCESS,
        'replyContent': {
            'remindedInds': ', '.join(remindedInd)
        }
    })


adminMsgHandlerMapping = {
    'r': adm_reminder
}
