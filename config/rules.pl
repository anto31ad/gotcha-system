% base facts

:- dynamic event/4.
:- dynamic blacklisted/1.

super_user(root).
super_user(admin).

action(login).
action(logout).
action(edit).

night_time(TimeStr) :-
    sub_atom(TimeStr, 0, 2, _, HourAtom),
    atom_number(HourAtom, Hour),
    Hour < 6.

% base anomaly rules

edit_night_time(Time) :-
    event(_, Time, _, edit),
    night_time(Time).

edit_from_unauthorized_user(User) :-
    event(_, _, User, edit),
    \+ super_user(User).

superuser_login_night_time(User, Time) :-
    event(_, Time, User, edit),
    super_user(User),
    night_time(Time).

blacklisted_user(User) :-
    event(_, _, User, _),
    blacklisted(User).

% anomaly wrappers

anomaly(edit_night_time, Time) :-
    edit_night_time(Time).

anomaly(edit_from_unauthorized_user, User) :-
    edit_from_unauthorized_user(User).

anomaly(superuser_login_night_time, (User, Time)) :-
    superuser_login_night_time(User, Time).

anomaly(blacklisted_user, User) :-
    blacklisted_user(User).
