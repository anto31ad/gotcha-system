from pyswip import Prolog
from pathlib import Path

def infer(facts_path: Path, rules_path: Path, **kwargs) -> list:
    prolog = Prolog()
    prolog.consult(rules_path.resolve())
    prolog.consult(facts_path.resolve())

    query_str = 'anomaly(Date, Time, User, IP, Reason)'

    # Dynamically modify the query based on the provided kwargs
    for key, value in kwargs.items():
        # Replace the placeholders with the appropriate values
        if key == 'date':
            query_str = query_str.replace('Date', value)
        elif key == 'time':
            query_str = query_str.replace('Time', value)
        elif key == 'user':
            query_str = query_str.replace('User', value)
        elif key == 'ip':
            query_str = query_str.replace('IP', value)
        elif key == 'reason':
            query_str = query_str.replace('Reason', value)

    response = prolog.query(query_str)

    transactions = []
    for row in response:
        transactions.append(row)

    return transactions
