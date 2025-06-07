from pyswip import Prolog

from .schema import Event, UserAction, SuspiciousEvent

def _convert_event_to_prolog_fact(event: Event) -> str | None:
    
    try:
        return (
            f'unprocessed_event('
            f'"{event.date}", '
            f'{event.time}, '
            f'{event.user}, '
            f'{event.action.value})'
        )
    except:
        return None

def update_kb(event: Event, prolog: Prolog):
    # update the user status
    online_user_fact = f'online_user({event.user})'
    user_is_online = len(list(prolog.query(online_user_fact))) > 0    

    if event.action == UserAction.LOGIN and not user_is_online:
        prolog.assertz(online_user_fact)
    elif event.action == UserAction.LOGOUT and user_is_online:
        prolog.retract(online_user_fact)


def check_event_using_inference(
        event: Event,
        prolog: Prolog,
    ) -> list[str]:

    anomalies = []

    fact = _convert_event_to_prolog_fact(event)
    if not fact:
        # some field of event is None or invalid
        raise ValueError()

    # asks prolog if the event has any anomalies
    prolog.assertz(fact)
    response = prolog.query('anomaly(Type, Info)')

    # if there are any anomalies, append their codename to the list
    for item in response:
        anomalies.append(item['Type'])

    # After all listings, the current fact can be removed because the event is no longer unprocessed
    # Removing it before will result in an empty response because prolog will see no fact.
    prolog.retract(fact)

    update_kb(event, prolog)
 
    return anomalies
