import csv
import random
from datetime import datetime, timedelta

from schema import EVENT_SCHEMA
from main import TEST_LOG_PATH

# Parameters
num_rows = 100  # you can change this to generate more or fewer rows

# Sample data pools
users = ["alice", "bob", "root", "admin", "carol", "eve", "mallory"]
request_types = ["login", "logout", "edit"]
private_ips = ["192.168.1.12", "10.0.0.5", "172.16.0.2"]
public_ip_pool = lambda: f"{random.randint(1, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(1, 254)}"

# Function to generate a random datetime string
def random_date(start, end):
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    date = start + timedelta(seconds=random_seconds)
    return date.strftime("%Y-%m-%d"), date.strftime("%H:%M")

# Generate CSV
with open(TEST_LOG_PATH.resolve(), mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(EVENT_SCHEMA)

    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 4, 11)

    for _ in range(num_rows):
        date_str, time_str = random_date(start_date, end_date)
        user = random.choice(users)
        ip = random.choice(private_ips) if random.random() < 0.3 else public_ip_pool()
        request_type = random.choice(request_types)
        writer.writerow([date_str, time_str, ip, user, request_type])

print(f"Generated {num_rows} rows")
