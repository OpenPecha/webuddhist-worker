from enum import StrEnum


class ReminderStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    CANCELLED = "cancelled"


class PushPlatform(StrEnum):
    ANDROID = "android"
    IOS = "ios"
