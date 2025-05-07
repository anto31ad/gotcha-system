import csv
import random
from datetime import datetime, timedelta
from enum import Enum

from app.schema import Event
from app.paths import TEST_LOG_PATH

# Parameters
num_rows = 100  # you can change this to generate more or fewer rows

# Sample data pools
users = ["alice", "bob", "root", "admin", "carol", "eve", "mallory"]
superusers = ['admin', 'root']

class UserAction(Enum):
    LOGIN = 'login'
    LOGOUT = 'logout'
    EDIT = 'edit'
    NONE = 'none'

def generate_realistic_events(target_num_of_items: int):
    current_datetime = datetime.now()

    online_users = set()
    count = 0

    while count <= target_num_of_items:
        user = random.choice(users)
        user_is_online = user in online_users

        if user in superusers:
            action = pick_next_super_user_action(user_is_online)
        else:
            action = pick_next_unpriviledged_user_action(user_is_online)

        if action == UserAction.NONE:
            continue
        elif action == UserAction.LOGIN:
            online_users.add(user)
        elif action == UserAction.LOGOUT:
            online_users.remove(user)

        # advance time by a random amount of minutes
        random_minutes = random.randint(0, 15)
        time_delta = timedelta(minutes=random_minutes)
        current_datetime += time_delta

        count += 1
        yield Event(
            date=current_datetime.strftime('%Y-%m-%d'),
            time=current_datetime.strftime('%H:%M'),
            user=user,
            action=action.value
            )

    while len(online_users) > 0:
        user = online_users.pop()
        yield Event(
            date=current_datetime.strftime('%Y-%m-%d'),
            time=current_datetime.strftime('%H:%M'),
            user=user,
            action=UserAction.LOGOUT
        )


def pick_next_super_user_action(online: bool):
    if not online:
        return UserAction.LOGIN
    # else
    perc = random.random()
    if perc < 0.01:
        return UserAction.LOGIN
    elif perc < 0.30:
        return UserAction.LOGOUT
    elif perc < 0.80:
        return UserAction.EDIT
    else:
        return UserAction.NONE

def pick_next_unpriviledged_user_action(online: bool):
    if not online:
        return UserAction.LOGIN
    # else
    perc = random.random()
    if perc < 0.01:
        return UserAction.LOGIN
    elif perc < 0.06:
        return UserAction.EDIT
    elif perc < 0.50:
        return UserAction.LOGOUT
    else:
        return UserAction.NONE
   

# Generate CSV
with open(TEST_LOG_PATH.resolve(), mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(Event.__annotations__.keys())

    data = generate_realistic_events(100) 

    count = 0
    for event in data:
        writer.writerow([
            event.date,
            event.time,
            event.user,
            event.action
        ])
        count += 1

print(f"Generated {count} rows")


# def generate_action_sequence(super_user: bool):

#     if super_user:
#         actions_weight = [
#             0.05, # login
#             0.35, # logout
#             0.60, # edit
#         ]
#     else:
#         actions_weight = [
#             0.05, # login
#             0.45, # logout
#             0.50, # edit
#         ]

#     possible_actions = [member for member in UserAction]
#     sequence = []
#     time_deltas = []
#     loop = True
#     while loop:
#         next_action = random.choices(possible_actions, weights=actions_weight, k=1)
#         sequence.append(next_action)

#         random_minutes = random.randint(0, 15)
#         time_deltas.append(timedelta(minutes=random_minutes))
        
#         loop = next_action != UserAction.LOGOUT

#     return {
#         sequence: sequence,
#         time_deltas: time_deltas
#     }
