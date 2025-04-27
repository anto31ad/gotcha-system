from io import TextIOWrapper

from pyswip import Prolog

from .schema import Event, ProcessedEvent

def process_event(
        event_dict: dict,
        prolog: Prolog,
        facts_file: TextIOWrapper,
        past_decision_file: TextIOWrapper) -> list:

    anomalies = []
    event = Event(**event_dict)
    fact = event.convert_to_prolog_fact()
    prolog.assertz(fact)

    response = prolog.query('anomaly(Type, Info)')

    sus = False
    for item in response:
        anomalies.append(item)
        sus = True

    # After all listings, the current fact can be removed.
    # Removing it before will result in an empty response because prolog will see no fact.
    prolog.retract(fact)
    # write the fact in the knowledge base
    facts_file.write(fact + '.\n') # TODO why no error? how does it get facts_file?

    # Now update the status
    active_user_fact = f'active({event.user})'
    if event.action == 'login':
        prolog.assertz(active_user_fact)
    elif event.action == 'logout' and list(prolog.query(active_user_fact)):
        prolog.retract(active_user_fact)

    past_decision_file.write(ProcessedEvent(suspicious=sus, **event_dict).convert_to_fact())
    return anomalies
