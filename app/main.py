from pyswip import Prolog

from .test import generate_events_to_file
from .control import monitor_manifesto, train
from .learning import get_user_predictors

from .paths import (
    BASE_RULES_PATH,
    BLACKLIST_PATH,
    TEST_LOG_PATH,
    EVENT_EXAMPLES_PATH
)

def main_menu_loop(prolog):

    predictors = get_user_predictors()

    while True:
        print("Choose next operation by typing (what's inside) :")
        print("  (s)    Start monitoring events")
        print(f"  (t)    Train an anomaly predictor for each user based on past events (reads from '{EVENT_EXAMPLES_PATH}')")
        print(f"  (tdel) Delete predictors")
        print(f"  (gen)  Test the generator of events (writes to '{TEST_LOG_PATH}')")
        print(f"  (rst)  Delete past events data (deletes file '{EVENT_EXAMPLES_PATH}')")
        print("  (q)    quit")

        input_value = input().lower()
        if input_value == 's':
            monitor_manifesto(prolog, predictors)
            break
        elif input_value == 't':
            train()
            predictors = get_user_predictors()
            break
        elif input_value == 'tdel':
            # TODO delete
            break
        elif input_value == 'rst':
            # TODO delete events
            break
        elif input_value == 'gen':
            generate_events_to_file(10)
            break
        elif input_value == 'q':
            return True
        else:
            print("Invalid input. Valid Options:")
    return False

if __name__ == "__main__":
    try:
        prolog = Prolog()
        prolog.consult(BASE_RULES_PATH.resolve())
        prolog.consult(BLACKLIST_PATH.resolve())

        quit = False
        while not quit:
            print(
                "=== Gotcha! (Main Menu) ===\n"
                "Target system: Manifesto\n\n")
            
            quit = main_menu_loop(prolog)
            print('')

    except KeyboardInterrupt:
        print("Shutting down...")
