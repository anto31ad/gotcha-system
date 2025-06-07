from .schema import SuspiciousEvent
from datetime import datetime, timedelta
from pyswip import Prolog
from collections import deque

from .paths import (
    BASE_RULES_PATH,
    BLACKLIST_PATH,
)

from .schema import(
    SuspiciousEvent,
    Event
)
from .logic import check_event_using_inference
from .utils import minutes_to_hhmm
from . import manifesto as Manifesto

def _process_suspicious_events(
        queue: deque[SuspiciousEvent],
        iteration_num: int,
):
    num_of_sus = len(queue)
    index = 0  

    while len(queue) > 0:
        event = queue.popleft()
        anomalies_list = []
        for codename in event.anomalies:
            anomalies_list.append(
                f"- {codename}")

        anomaly_desc = '\n'.join(anomalies_list)
        index += 1

        print(
            f"ITERATION {iteration_num}:\n"
            f"-------------\n"
            f"Suspicious event no. {index} out of {num_of_sus}:\n"
            f"-------------\n"
            f"datetime: {event.date} @ {minutes_to_hhmm(event.time)}\n"
            f"user: {event.user}\n"
            f"action: {event.action.value}\n\n"
            f"anomalies found:\n{anomaly_desc}\n\n"
            f"-------------\n"
            f"See next (Enter)\n"
        )

        while True:
            input_value = input()

            if input_value == '':
                break
            else:
                print('Invalid input')


def _continue_with_next_iteration() -> bool:
    print("Iteration completed.\n"
                  "Press 'Enter' to continue, or 'b' to go back.")

    input_value = None
    while True:

        input_value = input()

        if input_value == '':
            return True
        elif input_value == 'b':
            return False
        else:
            print('Invalid input')


def monitor_manifesto(debug_mode: bool = False):
    try:
        prolog = Prolog()
        prolog.consult(BASE_RULES_PATH.resolve())
        prolog.consult(BLACKLIST_PATH.resolve())

        time_of_day = datetime.now()
        iterations_done = 0
        sus_events: deque[SuspiciousEvent] = deque()
        iterate = True
        while iterate:
            # ask Manifesto for new events (Monitoring) until at least one suspicious pops up 
            while len(sus_events) < 1:
                new_events, minutes_elapsed = Manifesto.get_next_events(
                    time_of_day, debug=debug_mode)
                # advance time
                time_of_day += timedelta(minutes=minutes_elapsed)

                for event in new_events:
                    inferred_anomalies = check_event_using_inference(event, prolog)
                    if inferred_anomalies:
                        sus_events.append(
                            SuspiciousEvent(
                                anomalies=inferred_anomalies,
                                **event.model_dump()
                            ))
            
            iterations_done += 1
            _process_suspicious_events(sus_events, iterations_done)
            iterate = _continue_with_next_iteration()

    except KeyboardInterrupt:
        print('\nGoing back...')
