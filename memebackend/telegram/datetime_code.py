from datetime import datetime, timedelta

# Get today's date
today_str = datetime.now().strftime('%Y-%m-%d')
print("today:  ", today_str)

today_datetime = datetime.strptime(today_str, '%Y-%m-%d')
print("today:  ", today_datetime)

# Convert the datetime object to a timestamp
# today_timestamp = int(today_datetime.timestamp())
# print("today:  ", today_timestamp)

# Insert appointments for the next day
appointment_date = (today_datetime + timedelta(days=1)).strftime('%Y-%m-%d')
print("today:  ", appointment_date)

