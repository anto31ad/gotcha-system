import csv
from pathlib import Path

def parse_log(log_path: Path, output_path: Path):
    with open(log_path.resolve(), newline='') as csvfile, open(output_path, "w") as output_file:
        reader = csv.DictReader(csvfile)
        for row in reader:
            output_file.write(f'event("{row["date"]}", "{row["time"]}", {row["action"]}, {row["user"]}, "{row["ip"]}").\n')
