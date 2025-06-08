% base facts

:- dynamic unprocessed_event/4.
:- dynamic blacklisted/1.
:- dynamic online_user/1.

super_user(root).
super_user(admin).

night_time(MinutesPastMidnight) :-
    MinutesPastMidnight >= 0,
    MinutesPastMidnight < 360.

% base anomaly rules

double_login(User) :-
    unprocessed_event(_, _, User, login),
    online_user(User).

double_logout(User) :-
    unprocessed_event(_, _, User, logout),
    \+ online_user(User).

blacklisted_user(User) :-
    unprocessed_event(_, _, User, _),
    blacklisted(User).

edit_night_time(Time) :-
    unprocessed_event(_, Time, _, edit),
    night_time(Time).

edit_from_unauthorized_user(User) :-
    unprocessed_event(_, _, User, edit),
    \+ super_user(User).

edit_after_logout(User) :-
    unprocessed_event(_,_, User, edit),
    \+ online_user(User).

superuser_login_at_night_time(User, Time) :-
    unprocessed_event(_, Time, User, login),
    super_user(User),
    night_time(Time).

% anomaly wrappers

anomaly(edit_night_time, Time) :-
    edit_night_time(Time).

anomaly(edit_from_unauthorized_user, User) :-
    edit_from_unauthorized_user(User).

anomaly(edit_after_logout, User) :-
    edit_after_logout(User).

anomaly(superuser_login_at_night_time, (User, Time)) :-
    superuser_login_at_night_time(User, Time).

anomaly(blacklisted_user, User) :-
    blacklisted_user(User).

anomaly(double_login, User) :-
    double_login(User).

anomaly(double_logout, User) :-
    double_logout(User).
