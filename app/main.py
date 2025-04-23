import csv

from pathlib import Path
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

if __name__ == "__main__":
    print("\n🔍 Anomalie rilevate:\n")

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
    log_reader= csv.DictReader(log_file)

    row_no = 1
    for row in log_reader:
        fact = Event(**row).convert_to_prolog_fact()
        prolog.assertz(fact)
        
        facts_file.write(fact + '.\n')
        response = prolog.query('anomaly(Type, Info)')
                

        sus = False
        for index, item in enumerate(response):
            print(f"{row_no}/{index}: {item}")
            sus = True

        # After all listings, the current fact can be removed.
        # Removing it before will result in an empty response because prolog will see no fact.
        prolog.retract(fact)

        past_decision_file.write(ProcessedEvent(suspicious=sus, **row).convert_to_fact())

        row_no += 1

    past_decision_file.close()
    facts_file.close()
    log_file.close()
