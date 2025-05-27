import csv

from io import TextIOWrapper
from pyswip import Prolog

from .schema import(
    ProcessedEvent,
    Event,
    SuspiciousEvent
)
from .paths import (
    BASE_RULES_PATH,
    BLACKLIST_PATH,
    PAST_DECISIONS_PATH,
    FACTS_PATH,
    TEST_LOG_PATH
)
from .logic import process_event
from .control import process_suspicious_events

if __name__ == "__main__":

    try:
        prolog = Prolog()
        prolog.consult(BASE_RULES_PATH.resolve())
        prolog.consult(BLACKLIST_PATH.resolve())

        # past_decisions_header = ''

        # if not PAST_DECISIONS_PATH.exists():
        #     past_decisions_header = ', '.join(ProcessedEvent.model_fields.keys()) + '\n'

        # past_decision_file: TextIOWrapper = open(PAST_DECISIONS_PATH.resolve(), "a")
        # past_decision_file.write(past_decisions_header)

        facts_file: TextIOWrapper = open(FACTS_PATH.resolve(), "w")

        log_file: TextIOWrapper = open(TEST_LOG_PATH.resolve(), "r")
        log_reader = csv.DictReader(log_file)

        suspicious_events: dict[int, SuspiciousEvent] = {}
        row = 1
        for log_row in log_reader:
            processed_event: SuspiciousEvent = process_event(Event(**log_row), prolog)

            if processed_event.anomalies: # list not empty
                suspicious_events[row] = processed_event

            row += 1

        process_suspicious_events(suspicious_events)

    except KeyboardInterrupt:
        print('\nShutting down...')

    finally:
        #past_decision_file.close()
        facts_file.close()
        log_file.close()
