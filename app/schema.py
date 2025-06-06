from enum import Enum
from pydantic import BaseModel

EVENT_SCHEMA: list[str] = ["date", "time", "ip", "user", "action"]

class UserAction(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    EDIT = 'edit'
    NONE = None

class Event(BaseModel):
    date: str | None = None
    time: int | None = None
    user: str | None = None
    action: UserAction = UserAction.NONE

class SuspiciousEvent(Event):
    anomalies: list[str]

class ProcessedEvent(Event):
    suspicious: bool = False

    def convert_to_fact(self):
        return (
            f'"{self.date}", '
            f'"{self.time}", '
            f'"{self.user}", '
            f'"{self.action}", '
            f'"{self.suspicious}"\n'
        )
