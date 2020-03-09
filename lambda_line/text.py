from typing import Dict


class LINE_MESSAGE_TEXTS():
    HOMEWORK_NO_RECORD = 'homework_no_record'
    CLASS_HISTORY_NO_RECORD = 'class_history_no_record'
    NEXT_CLASS_NO_RECORD = 'next_class_no_record'
    NEXT_CLASS_RECORD = 'next_class_record'
    FOLLOW_GREETING = 'follow_greeting'
    REMINDER_SUCCESS = 'reminder_success'


def messageText(id, content: Dict):
    M = LINE_MESSAGE_TEXTS

    # If not mapped, use id itself (support direct injection in linebot)
    textFrame = {
        M.HOMEWORK_NO_RECORD: 'We don\'t have record of your homework 😢.',
        M.CLASS_HISTORY_NO_RECORD: 'We don\'t have record of your past classes 😢.',
        M.NEXT_CLASS_NO_RECORD: 'We don\'t have record of your next class 😢.',
        M.NEXT_CLASS_RECORD: lambda x: 'Your next class is {classTime} at {classLocation}. Your trainer is {classTrainer} 😉.'.format(**x),
        M.FOLLOW_GREETING: lambda x: 'Hello, {userName} 😄.'.format(**x),
        M.REMINDER_SUCCESS: lambda x: 'Reminder sent to {remindedInds}.'.format(**x)
    }.get(id, id)

    # Delay extracting the content
    return textFrame(content) if callable(textFrame) else textFrame
