import csv
import random
from datetime import datetime, timedelta

# Parameters
num_rows = 100  # you can change this to generate more or fewer rows

filename = "data/generated/test_log.csv"

# Sample data pools
users = ["alice", "bob", "root", "admin", "carol", "eve", "mallory"]
actions = ["login", "logout", "file_access", "config_change"]
event_types = ["normal", "suspicious"]
private_ips = ["192.168.1.12", "10.0.0.5", "172.16.0.2"]
public_ip_pool = lambda: f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

# Function to generate a random datetime string
def random_date(start, end):
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    date = start + timedelta(seconds=random_seconds)
    return date.strftime("%Y-%m-%d"), date.strftime("%H:%M")

# Generate CSV
with open(filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["date", "user", "time", "ip", "action", "event_type"])

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 4, 11)

    for _ in range(num_rows):
        date_str, time_str = random_date(start_date, end_date)
        user = random.choice(users)
        ip = random.choice(private_ips) if random.random() < 0.3 else public_ip_pool()
        action = random.choice(actions)
        event_type = "suspicious" if random.random() < 0.2 else "normal"
        writer.writerow([date_str, user, time_str, ip, action, event_type])

print(f"Generated {num_rows} rows in {filename}")
