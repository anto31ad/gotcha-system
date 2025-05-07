from io import TextIOWrapper

from pyswip import Prolog

from .schema import Event, ProcessedEvent

def process_event(
        event: Event,
        prolog: Prolog,
        facts_file: TextIOWrapper,
        past_decision_file: TextIOWrapper) -> list:

    anomalies = []
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
    facts_file.write(fact + '.\n')

    # Now update the status
    online_user_fact = f'online_user({event.user})'
    if event.action == 'login':
        prolog.assertz(online_user_fact)
    elif event.action == 'logout' and list(prolog.query(online_user_fact)):
        prolog.retract(online_user_fact)

    #past_decision_file.write(ProcessedEvent(suspicious=sus, **event.model_dump()).convert_to_fact())
    return anomalies
