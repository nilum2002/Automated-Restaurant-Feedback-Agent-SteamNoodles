from datetime import datetime, timedelta
from random import randint

# Start and end dates
start_date = datetime(2024, 1, 1)
end_date = datetime(2025, 8, 15)

# Increment step (1 day)




date_time_list = []
current_date = start_date
while current_date <= end_date:
    # random hour, minute, second
    hour = randint(0, 23)
    minute = randint(0, 59)
    second = randint(0, 59)
    date_time = current_date.replace(hour=hour, minute=minute, second=second)
    date_time_str = str(date_time)
    date_time_list.append(date_time_str)
    current_date += timedelta(days= randint(1,30))

# Print first 10 for verification
print(date_time_list)
print(f"Total date-time entries: {len(date_time_list)}")
