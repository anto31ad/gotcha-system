import csv
from datetime import datetime, timedelta

from . import manifesto as Manifesto
from .schema import Event
from .paths import TEST_LOG_PATH

def generate_events_to_file(iterations: int):

    with open(TEST_LOG_PATH.resolve(), mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(Event.__annotations__.keys())

        time_of_day = datetime.now()
        for i in range(0, iterations):

            events, minutes_elapsed = Manifesto.get_next_events(time_of_day)
            time_of_day += timedelta(minutes=minutes_elapsed)

            for event in events:
                writer.writerow([
                    event.date,
                    event.time,
                    event.user,
                    event.action.value
                ])
