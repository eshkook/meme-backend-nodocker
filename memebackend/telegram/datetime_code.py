from datetime import datetime, timedelta

# Get today's date
today_str = datetime.now().strftime('%Y-%m-%d')
print("today:  ", today_str)

today_datetime = datetime.strptime(today_str, '%Y-%m-%d')
print("today_datetime:  ", today_datetime)

# Insert appointments for the next day
appointment_date = (today_datetime + timedelta(days=1))
print("appointment_date:  ", appointment_date)

diff_seconds = abs((appointment_date - today_datetime).total_seconds())

# Convert seconds to hours
diff_hours = diff_seconds / 3600

print(diff_hours<87)


now_datetime = datetime.now()
today_at_9_datetime = now_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
print(today_at_9_datetime)
slots_list = []
# slots_list += [for work_hours in range(9) if ]
for work_hours in range(9):
    potential_slot_datetime = today_at_9_datetime + timedelta(hours=work_hours)
    if now_datetime < potential_slot_datetime:
        slots_list.append(potential_slot_datetime.strftime('%Y-%m-%d %H%M'))

print(slots_list)        
