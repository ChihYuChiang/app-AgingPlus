import os
import sys
import re
import logging
from linebot import WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import FollowEvent, MessageEvent, TextMessage, PostbackEvent
from handlers_postback import postbackHandlerMapping
from handlers_adminMsg import adminMsgHandlerMapping
from util import LogMsg, Logger, LAMBDA_NAME, HANDLER_STAGE as HS
from util import invokeLambda, AIR_EVENT_TYPES, LINE_EVENT_TYPES, LAMBDAS
from util import LINE_MESSAGE_TEXTS
# https://github.com/line/line-bot-sdk-python
# https://developers.line.biz/en/reference/messaging-api/


# -- Setup
# TODO: encrypt keys on AWS
# TODO: mypy when matured
# TODO: pytest with testing db
# TODO: lambda layer to share enum and others
# Logger
logger = Logger(LAMBDA_NAME, (logging.StreamHandler(), logging.DEBUG))

# Get channel_secret from environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)

# Line webhook
line_handler = WebhookHandler(channel_secret)


# -- Main handler
def lambda_handler(requestEvent, context):
    # Get X-Line-Signature header value
    signature = requestEvent['headers']['X-Line-Signature']

    # Get request body as text
    body = requestEvent['body']

    # Give logger `lineUserId` info
    logger.setLineUserId(body.source.user_id)

    # Check the body-signature matches and handle the event
    try: line_handler.handle(body, signature)
    except InvalidSignatureError:
        logger.error('Invalid signature. Please check your channel access token/channel secret.')
        raise

    return {'statusCode': 200, 'body': 'OK'}


# -- Handle PostbackEvent type
@line_handler.add(PostbackEvent)
def handle_postback(event):
    eventAction = re.search('action=(.+?)(;|$)', event.postback.data)[1]
    logger.debug(LogMsg(
        PostbackEvent,
        stage=HS.STARTING_HANDOVER,
        eventAction=eventAction
    ))

    postbackHandler = postbackHandlerMapping[eventAction]
    logger.info(LogMsg(postbackHandler, stage=HS.STARTING))
    postbackHandler(event)
    logger.debug(LogMsg(postbackHandler, stage=HS.FINISHED))


# -- Handle MessageEvent and TextMessage type
@line_handler.add(MessageEvent, TextMessage)
def handle_message(event):
    # When receiving special msg, inspect admin identity, and invoke admin cmd
    adminHandler = adminMsgHandlerMapping.get(event.message.text)
    if adminHandler and invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.IS_ADMIN,
        'lineUserId': event.source.user_id
    }):
        logger.info(LogMsg(adminHandler, stage=HS.STARTING))
        adminHandler(event)
        logger.debug(LogMsg(adminHandler, stage=HS.FINISHED))

    # If not admin command, respond with default
    else:
        logger.info(LogMsg(
            MessageEvent,
            stage=HS.STARTING,
            msgContent=event.message.text
        ))

        # TODO: Better default reply
        # Default reply replicates the incoming message
        invokeLambda(LAMBDAS.LINE, {
            'eventType': LINE_EVENT_TYPES.REPLY,
            'lineReplyToken': event.reply_token,
            'replyMessage': event.message.text
        })
        logger.debug(LogMsg(MessageEvent, stage=HS.FINISHED))


# -- Handle FollowEvent (when someone adds this account as friend)
@line_handler.add(FollowEvent)
def handle_follow(event):
    logger.info(LogMsg(FollowEvent, stage=HS.STARTING))
    resPayload = invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.GET_PROFILE,
        'lineUserId': event.source.user_id
    })
    userDisplayName = resPayload['Data']['displayName']
    userProfilePic = resPayload['Data']['pictureUrl']

    logger.debug(LogMsg(
        FollowEvent,
        stage=HS.IN_PROCESS,
        userDisplayName=userDisplayName
    ))
    invokeLambda(LAMBDAS.LINE, {
        'eventType': LINE_EVENT_TYPES.REPLY,
        'lineReplyToken': event.reply_token,
        'replyMessage': LINE_MESSAGE_TEXTS.FOLLOW_GREETING,
        'replyContent': {
            'userName': userDisplayName
        }
    })

    invokeLambda(LAMBDAS.AIRTABLE, {
        'eventType': AIR_EVENT_TYPES.FOLLOW,
        'lineUserId': event.source.user_id,
        'lineDisplayName': userDisplayName,
        'lineProfilePic': userProfilePic
    })
    logger.debug(LogMsg(FollowEvent, stage=HS.FINISHED))
