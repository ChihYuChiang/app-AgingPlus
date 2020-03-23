class EVENT_TYPES():
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
