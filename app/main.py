import csv

from datetime import datetime, timedelta
from io import TextIOWrapper
from pyswip import Prolog

from .schema import(
    SuspiciousEvent
)
from .paths import (
    BASE_RULES_PATH,
    BLACKLIST_PATH,
)
from .logic import process_event
from .control import process_suspicious_events
from . import manifesto as Manifesto
from .test import generate_events_to_file

if __name__ == "__main__":

    try:
        prolog = Prolog()
        prolog.consult(BASE_RULES_PATH.resolve())
        prolog.consult(BLACKLIST_PATH.resolve())

        time_of_day = datetime.now()
        suspicious_events: dict[int, SuspiciousEvent] = {}
        iterations_done = 0
        while True:
            # ask Manifesto for new events (Monitoring)
            new_events, minutes_elapsed = Manifesto.get_next_events(time_of_day, debug=True)
            time_of_day += timedelta(minutes=minutes_elapsed)

            row = 1
            for event in new_events:
                processed_event: SuspiciousEvent = process_event(event, prolog)
                
                # TODO if model for user exists, run model and append any anomalies

                if processed_event.anomalies: # list not empty
                    suspicious_events[row] = processed_event

                row += 1
            
            process_suspicious_events(suspicious_events, iterations_done + 1)

            # TODO ask if gotcha user wants to continue or train the models
            iterations_done += 1

    except KeyboardInterrupt:
        print('\nShutting down...')

    finally:
        pass
