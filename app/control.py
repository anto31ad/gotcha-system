from .schema import SuspiciousEvent

def process_suspicious_events(
        anomalies: dict[int, SuspiciousEvent],
        iteration_number: int,
):
    num_of_anomalies = len(anomalies)
    index = 0  
    for key, event in anomalies.items():
        anomalies_list = []
        for codename in event.anomalies:
            anomalies_list.append(
                f"- {codename}")

        anomaly_desc = '\n'.join(anomalies_list)
        valid_command = False
        index += 1

        print(
            f"ITERATION {iteration_number}:\n"
            f"Suspicious event no. {index} out of {num_of_anomalies}:\n"
            f"-------------\n"
            f"row: {key}\n"
            f"datetime: {event.date} {event.time}\n"
            f"user: {event.user}\n"
            f"action: {event.action.value}\n\n"
            f"anomalies found:\n{anomaly_desc}\n\n"
            f"-------------\n"
            f"See next (Enter)\n"
        )

        while not valid_command:
            input_value = input()
            if input_value == '':
                valid_command = True
            else:
                print('Invalid input\n')
