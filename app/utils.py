import csv
import numpy as np
import pandas as pd

from datetime import timedelta, datetime
from pathlib import Path

from .schema import Event, UserAction


def minutes_to_hhmm(minutes: int) -> str:
    hours = minutes // 60 % 24
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def sincos_to_minutes(sin_val, cos_val):
    # get angle in radians (0 to 2*pi)
    angle = np.arctan2(sin_val, cos_val)
    # convert negative angle to positive angle
    if angle < 0:
        angle += 2 * np.pi

    fraction = angle / (2 * np.pi)

    return int(round(fraction * 1440))


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


def get_next_day_from_past_events(filepath: Path):

    if not filepath.exists():
        return datetime.today() + timedelta(hours=6)

    df = pd.read_csv(filepath.resolve())
    last_date = pd.to_datetime(df["date"]).max()
    return last_date + timedelta(days=1, hours=6)
