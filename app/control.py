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

MAX_ITERATIONS = 15

def _process_suspicious_events(
        queue: deque[SuspiciousEvent],
        iteration_num: int,
        normal_events: list[Event]
):

    false_positives: list[Event] = []
    queue_len = len(queue)

    if queue_len < 1:
        return

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
    time_of_day = datetime.now()
    iterations_done = 0
    sus_events: deque[SuspiciousEvent] = deque()
    iterate = True

    while iterate:
        normal_events: list[Event] = []
        
        # MAX_ITERATIONS prevents infinite cycling if no suspicious events are found
        #   for ex. when disabling inference and predictors
        has_hit_max_iterations = False
        iterations_without_hits = 0
        # ask Manifesto for new events (Monitoring) until at least one suspicious pops up 
        while len(sus_events) < 1:
            iterations_without_hits += 1
            has_hit_max_iterations = iterations_without_hits >= MAX_ITERATIONS
            
            if has_hit_max_iterations:
                print("Reached max iterations when asking Manifesto for events")
                break

            new_events, minutes_elapsed = Manifesto.get_next_events(
                time_of_day, debug=debug_mode)
            # advance time
            time_of_day += timedelta(minutes=minutes_elapsed)

            for event in new_events:
                inferred_anomalies = check_event_using_inference(event, prolog)
                predicted_anomalies = check_event_using_predictor(predictors, event)
                anomalies =  inferred_anomalies + predicted_anomalies
                if anomalies:
                    sus_events.append(
                        SuspiciousEvent(
                            anomalies=anomalies,
                            **event.model_dump()))
                else:
                    normal_events.append(event)
        

        # let the user decide if suspicious events are true positives or false positives;
        # false positives extend the normal_events list, which will be later serialized
        _process_suspicious_events(sus_events, iterations_done, normal_events)
        _serialize_event_examples(normal_events)

        if not has_hit_max_iterations:
                print("(!) ITERATION COMPLETED (!)\n")

        print("Press Enter to continue, or 'B' to go back.")

        iterate = _continue_with_next_iteration()
        iterations_done += 1


def train():
    event_examples = parse_events_from_csv(EVENT_EXAMPLES_PATH)

    events_size = len(event_examples)
    if events_size < 1:
        print("No past events found!")
    elif events_size < 100:
        print(f"There are just {events_size} events in past data. Wait for at least 100")
    else:
        print("Starting training...")
        train_user_models(event_examples)

    # wait for user input before returning
    while True:
        print("Press Enter to go back.")
        input_value = input()
        if input_value == '':
            break
