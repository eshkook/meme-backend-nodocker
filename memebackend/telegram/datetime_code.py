from datetime import datetime, timedelta
import dateutil.tz

# Get today's date
today_str = datetime.now().strftime("%Y-%m-%d")
print("today_str:  ", today_str)

today_datetime = datetime.strptime(today_str, "%Y-%m-%d")
print("today_datetime:  ", today_datetime)

# Insert appointments for the next day
appointment_date = today_datetime + timedelta(days=1)
print("appointment_date:  ", appointment_date)

diff_seconds = abs((appointment_date - today_datetime).total_seconds())

# Convert seconds to hours
diff_hours = diff_seconds / 3600

print("diff_hours:   ", diff_hours)

slots_list = []

now_datetime = datetime.now()
today_at_9_datetime = now_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
print("today_at_9_datetime:    ", today_at_9_datetime)

for work_hours in range(9):
    potential_slot_datetime = today_at_9_datetime + timedelta(hours=work_hours)
    if now_datetime < potential_slot_datetime:
        slots_list.append(potential_slot_datetime.strftime("%Y-%m-%d %H%M"))

print("slots_list:    ", slots_list)

tomorrow_at_9_datetime = today_at_9_datetime + timedelta(days=1)
print("tomorrow_at_9_datetime:    ", tomorrow_at_9_datetime)

for work_hours in range(9):
    slots_list.append(
        (tomorrow_at_9_datetime + timedelta(hours=work_hours)).strftime("%Y-%m-%d %H%M")
    )

print("full_slots_list:    ", slots_list)

print(type(datetime.strptime(slots_list[0], "%Y-%m-%d %H%M")))

print(
    (datetime.strptime(slots_list[4], "%Y-%m-%d %H%M")- datetime.strptime(slots_list[3], "%Y-%m-%d %H%M")).total_seconds()
)

# # Get today's date
# today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
# print("today_str:  ", today_str)

israel_tz = dateutil.tz.gettz('Asia/Jerusalem')
now_datetime = datetime.now(israel_tz).strftime("%Y-%m-%d %H:%M")
print("now_datetime:  ", now_datetime)

a=datetime.now(israel_tz)-datetime.strptime('2023-10-25 19:00', '%Y-%m-%d %H:%M').replace(tzinfo=israel_tz)

current_time = datetime.now(israel_tz)
next_hour_time = current_time.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
next_hour_time = next_hour_time.strftime("%Y-%m-%d %H:%M")
print(next_hour_time)

print(datetime.now(israel_tz).strftime('%A'))