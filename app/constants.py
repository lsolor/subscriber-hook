from enum import Enum

class EventType(str, Enum):
    USER_CREATED = "user.created"
    EMAIL_NOTIFICATION = "email.notification"


CORRELATION_HDR = "X-Correlation-Id"