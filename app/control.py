import csv

from collections import deque
from datetime import datetime, timedelta
from pyswip import Prolog

from .schema import SuspiciousEvent

from .paths import (
    EVENT_EXAMPLES_PATH,
)

from .schema import(
    SuspiciousEvent,
    Event
)
from .logic import check_event_using_inference
from .utils import minutes_to_hhmm, parse_events_from_csv
from .learning import (
    train_user_models,
    check_event_using_predictor
)
from . import manifesto as Manifesto

def _process_suspicious_events(
        queue: deque[SuspiciousEvent],
        iteration_num: int,
        normal_events: list[Event]
):

    false_positives: list[Event] = []
    queue_len = len(queue)
    while queue_len > 0:
        event = queue.popleft()

        anomalies_list = []
        for codename in event.anomalies:
            anomalies_list.append(
                f"- {codename}")

        anomaly_desc = '\n'.join(anomalies_list)

        print(
            f"=== ITERATION no. {iteration_num} ===\n"
            f"{queue_len} suspicious events left to process\n"
            f"-------------\n"
            "=== Current suspicious event ===\n\n"
            f"session_id: {event.session_id}\n"
            f"datetime: {event.date} @ {minutes_to_hhmm(event.time)}\n"
            f"user: {event.user}\n"
            f"action: {event.action.value}\n\n"
            f"anomalies found:\n{anomaly_desc}\n\n"
            f"-------------\n"
        )

        while True:
            print(f"Threat (Y), Not a threat (N), Handle later (Enter)\n")
            input_value = input().lower()

            if input_value == '':
                # enqueue the event again
                queue.append(event)
                break
            elif input_value == 'y':
                break
            elif input_value == 'n':
                false_positives.append(event)
                break
            else:
                print('Invalid input. Retry.')

        queue_len = len(queue)

    normal_events.extend(false_positives)


def _serialize_event_examples(events: list[Event]):
    
    if not events:
        return

    needs_header = not EVENT_EXAMPLES_PATH.exists()
    sorted_events = sorted(events, key=lambda event: (event.date, event.time))
    with open(EVENT_EXAMPLES_PATH.resolve(), mode='a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if needs_header:
            writer.writerow(Event.__annotations__.keys())

        for event in sorted_events:
            writer.writerow([
                event.session_id,
                event.date,
                event.time,
                event.user,
                event.action.value
            ])


def _continue_with_next_iteration() -> bool:
    print(
        "(!) ITERATION COMPLETED (!)\n"
        "Press Enter to continue, or 'B' to go back.")

    input_value = None
    while True:

        input_value = input().lower()

        if input_value == '':
            return True
        elif input_value == 'b':
            return False
        else:
            print('Invalid input')


def monitor_manifesto(prolog: Prolog, predictors: dict, debug_mode: bool = False):
    try:
        time_of_day = datetime.now()
        iterations_done = 0
        sus_events: deque[SuspiciousEvent] = deque()
        iterate = True
        normal_events: list[Event] = []
        while iterate:
            # ask Manifesto for new events (Monitoring) until at least one suspicious pops up 
            while len(sus_events) < 1:
                new_events, minutes_elapsed = Manifesto.get_next_events(
                    time_of_day, debug=debug_mode)
                # advance time
                time_of_day += timedelta(minutes=minutes_elapsed)

                for event in new_events:
                    inferred_anomalies = check_event_using_inference(event, prolog)
                    predicted_anomalies = check_event_using_predictor(predictors, event)
                    anomalies = inferred_anomalies + predicted_anomalies
                    if anomalies:
                        sus_events.append(
                            SuspiciousEvent(
                                anomalies=anomalies,
                                **event.model_dump()))
                    else:
                        normal_events.append(event)
            
            iterations_done += 1

            # let the user decide if suspicious events are true positives or false positives;
            # false positives extend the normal_events list, which will be later serialized
            _process_suspicious_events(sus_events, iterations_done, normal_events)
            _serialize_event_examples(normal_events)

            iterate = _continue_with_next_iteration()

    except KeyboardInterrupt:
        print('\nGoing back...')


def train():
    event_examples = parse_events_from_csv(EVENT_EXAMPLES_PATH)

    events_size = len(event_examples)
    if events_size < 1:
        print("No past events found!")
    elif events_size < 10:
        print(f"There are just {events_size} events in past data. Wait for at least 10.")
    else:
        print("Starting training...")
        train_user_models(event_examples)

    # wait for user input before returning
    while True:
        print("Press Enter to go back.")
        input_value = input()
        if input_value == '':
            break
