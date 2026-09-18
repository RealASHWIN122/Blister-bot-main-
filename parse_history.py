import datetime
import re

initial_date = datetime.datetime.strptime("2026-07-28", "%Y-%m-%d")

with open("history.txt", "r") as f:
    lines = f.readlines()

current_week = 0
weeks_data = {}

current_date = None
for line in lines:
    m = re.match(r"^commit .* \((.*)\)", line)
    if m:
        date_str = m.group(1)
        current_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
        delta = current_date - initial_date
        current_week = (delta.days // 7) + 1
        if current_week not in weeks_data:
            weeks_data[current_week] = set()
        continue
    
    m2 = re.match(r"^[AMR\d]+\s+(.*)", line)
    if m2 and current_week:
        file = m2.group(1)
        # Handle renames A -> B
        if '\t' in file:
            file = file.split('\t')[-1]
        weeks_data[current_week].add(file)

for week in sorted(weeks_data.keys()):
    print(f"--- Week {week} ---")
    files = list(weeks_data[week])
    for f in sorted(files)[:10]:
        print(f"  {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")

