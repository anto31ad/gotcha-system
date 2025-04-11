:- consult('axioms.pl').
:- consult('generated/facts.pl').

:- dynamic event/1.

% miscellaneous
night_time(TimeStr) :-
    sub_atom(TimeStr, 0, 2, _, HourAtom),
    atom_number(HourAtom, Hour),
    Hour < 6.

% anomaly detection
anomaly(Date, Time, User, IP, "Accesso da IP non riconosciuto") :-
    event(Date, Time, login, User, IP),
    \+ internal_IP(IP).

anomaly(Date, Time, User, IP, "Accesso notturno") :-
    event(Date, Time, login, User, IP),
    night_time(Time).

anomaly(Date, Time, User, IP, "User privilegiato attivo di notte") :-
    event(Date, Time, login, User, IP),
    priviledged_user(User),
    night_time(Time).
