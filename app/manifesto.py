import random
import string

from datetime import datetime, timedelta
from dataclasses import dataclass, field

@dataclass
class User:
    name: str = "unknown"
    is_super: bool = False
    time_ranges: list = field(default_factory=list)

from .schema import Event, UserAction

_users = [
    User(
        name='alice',
        is_super=False,
        time_ranges=[range(400, 780), range(860, 1100)]),
    User(
        name='bob',
        is_super=False,
        time_ranges=[range(450, 700), range(840, 1000), range(1200, 1250)]),
    User(
        name='eve',
        is_super=False,
        time_ranges=[range(450, 700), range(900, 1000), range(0, 120)]),
    User(
        name='carol',
        is_super=False,
        time_ranges=[range(500, 900), range(1000, 1200)]
    ),
    User(
        name='root',
        is_super=True,
        time_ranges=[range(0, 1440)]
    ),
    User(
        name='admin',
        is_super=True,
        time_ranges=[range(0, 1440)]
    ),
]

_nighttime_range_in_minutes = range(0, 360) # from midnight to 6AM
_session_id_char_pool = string.ascii_letters + string.digits

def _random_session_id():
    return ''.join(random.choices(_session_id_char_pool, k=8))


def _datestr_from_datetime(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d')


def _minutes_from_datetime(dt: datetime) -> int:
    return dt.hour * 60 + dt.minute


def _pick_next_super_user_action():
    perc = random.random()
    if perc < 0.01:
        return UserAction.LOGIN
    elif perc < 0.30:
        return UserAction.LOGOUT
    elif perc < 0.80:
        return UserAction.EDIT
    else:
        return UserAction.NONE


def _pick_next_unpriviledged_user_action():
    perc = random.random()
    if perc < 0.01:
        return UserAction.LOGIN
    elif perc < 0.06:
        return UserAction.EDIT
    elif perc < 0.50:
        return UserAction.LOGOUT
    else:
        return UserAction.NONE


def _generate_user_session(
        start_datetime: datetime,
        user: str,
        superuser: bool
    ) -> tuple[list[Event], int]:

    events: list[Event] = []
    session_id = _random_session_id()

    next_action_func = _pick_next_super_user_action \
        if superuser else _pick_next_unpriviledged_user_action
    
    tot_min_elapsed = 0
    cur_action = UserAction.LOGIN
    first_iteration = True
    while cur_action != UserAction.LOGOUT:
        
        tot_min_elapsed += random.randint(0, 120)
        
        if first_iteration:
            first_iteration = False
        else:
            cur_action = next_action_func()
            if cur_action == UserAction.NONE:
                continue

        # it is best to use timedelta to account for time deltas crossing the end of the day
        cur_datetime = start_datetime + timedelta(minutes=tot_min_elapsed)
        events.append( Event(
            session_id=session_id,
            date=_datestr_from_datetime(cur_datetime),
            time=_minutes_from_datetime(cur_datetime),
            user=user,
            action=cur_action))

    return (events, tot_min_elapsed)


def get_next_events(
        start_datetime: datetime,
        debug: bool = False,
    ) -> tuple[list[Event], int]:
    
    events: list[Event] = []
    minutes_past_midnight = _minutes_from_datetime(start_datetime)
    is_nighttime = minutes_past_midnight in _nighttime_range_in_minutes

    # during night time, there is less chance of user activity

    total_minutes_elapsed = 0
    for user in _users:

        # TODO use ranges
        is_their_timerange = any(minutes_past_midnight in r for r in user.time_ranges)

        if is_their_timerange:
            # superusers are thought to be less active than unpriviledged users 
            chance_of_inactivity = 0.4 if user.is_super else 0.2
        elif is_nighttime:
            chance_of_inactivity = 0.9
        else:
            chance_of_inactivity = 0.7

        random_perc = random.random()
        if random_perc < chance_of_inactivity:
            continue
        else:
            user_events, minutes_elapsed = _generate_user_session(start_datetime, user.name, user.is_super)
            total_minutes_elapsed = max(total_minutes_elapsed, minutes_elapsed) 
            events.extend(user_events)

    # sort events by datetime
    events.sort(key=lambda event: (event.date, event.time))

    if debug:
        for event in events:
            print(event.model_dump())

    return events, total_minutes_elapsed
