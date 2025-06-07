import csv

from pathlib import Path

from .schema import Event, UserAction


def minutes_to_hhmm(minutes: int) -> str:
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02d}"


def convert_timestr_to_min(timestr) -> int:
    hour, minute = map(int, timestr.split(":"))
    return hour * 60 + minute


def parse_events_from_csv(filepath: Path) -> list[Event]:

    if not filepath.exists():
        return []

    events = []
    with open(filepath.resolve(), "r") as file:
        for line in csv.DictReader(file):
            events.append(
                Event(
                    session_id=line['session_id'],
                    date=line['date'],
                    time=int(line['time']),
                    user=line['user'],
                    action=UserAction(line['action'])
                )
            )
    return events
