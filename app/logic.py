from io import TextIOWrapper
from pyswip import Prolog

from .schema import Event, ProcessedEvent, SuspiciousEvent

def process_event(
        event: Event,
        prolog: Prolog,
        facts_file: TextIOWrapper,
        #past_decision_file: TextIOWrapper = None,
    ) -> SuspiciousEvent:

    anomalies = []
    fact = event.convert_to_prolog_fact()
    prolog.assertz(fact)

    response = prolog.query('anomaly(Type, Info)')

    sus = False
    for item in response:
        anomalies.append(item['Type'])
        sus = True

    # After all listings, the current fact can be removed.
    # Removing it before will result in an empty response because prolog will see no fact.
    prolog.retract(fact)
    # write the fact in the knowledge base
    facts_file.write(fact + '.\n')

    # Now update the status

    online_user_fact = f'online_user({event.user})'
    user_is_online = len(list(prolog.query(online_user_fact))) > 0    
    if event.action == 'login' and not user_is_online:
        prolog.assertz(online_user_fact)
    elif event.action == 'logout' and user_is_online:
        prolog.retract(online_user_fact)

    #past_decision_file.write(ProcessedEvent(suspicious=sus, **event.model_dump()).convert_to_fact())
    return SuspiciousEvent(anomalies=anomalies, **event.model_dump())
