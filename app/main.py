import csv

from io import TextIOWrapper
from pyswip import Prolog

from .schema import ProcessedEvent, Event
from .paths import (
    BASE_RULES_PATH,
    BLACKLIST_PATH,
    PAST_DECISIONS_PATH,
    FACTS_PATH,
    TEST_LOG_PATH
)
from .logic import process_event

if __name__ == "__main__":

    prolog = Prolog()
    prolog.consult(BASE_RULES_PATH.resolve())
    prolog.consult(BLACKLIST_PATH.resolve())

    schema = Event.model_fields.keys()
    past_decisions_header = ''

    if not PAST_DECISIONS_PATH.exists():
        past_decisions_header = ', '.join(ProcessedEvent.model_fields.keys()) + '\n'

    past_decision_file: TextIOWrapper = open(PAST_DECISIONS_PATH.resolve(), "a")
    past_decision_file.write(past_decisions_header)

    facts_file: TextIOWrapper = open(FACTS_PATH.resolve(), "w")

    log_file: TextIOWrapper = open(TEST_LOG_PATH.resolve(), "r")
    log_reader = csv.DictReader(log_file)

    anomalies = {}
    row = 1
    for event_features in log_reader:
        event_anomalies = process_event(event_features, prolog, facts_file, past_decision_file)
        
        if event_anomalies: # list not empty
            anomalies[row] = event_anomalies

        row += 1

    print(f"Found {len(anomalies)} anomalies")
    
    for key, event in anomalies.items():
        event_anomalies_len = len(event) 
        for event_index, anomaly in enumerate(event):
            print(f"row: {key} - anomaly {event_index + 1}/{event_anomalies_len} - details: {anomaly}")

    past_decision_file.close()
    facts_file.close()
    log_file.close()
