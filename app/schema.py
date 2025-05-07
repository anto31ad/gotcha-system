from pydantic import BaseModel

EVENT_SCHEMA: list[str] = ["date", "time", "ip", "user", "action"]

class Event(BaseModel):
    date: str = ''
    time: str = ''
    user: str = ''
    action: str = ''

    def convert_to_prolog_fact(self) -> str:
        return (
            f'unprocessed_event('
            f'"{self.date}", '
            f'"{self.time}", '
            f'{self.user}, '
            f'{self.action})'
        )

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
