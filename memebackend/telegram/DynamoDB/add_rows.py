import boto3

table_name = "botox_table"
region_name = 'eu-west-1'

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name=region_name)
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table(table_name)

def create_entry():
    table.put_item(
        Item={
            'id': '2',  # Replace 'unique_id' with a unique value
            'timestamp': '2',  # Replace 'your_timestamp' with a timestamp value
            'a': 1,
            'b': 2,
            'c': 3
        }
    )



# Call the function to add a single row
create_entry()


# import boto3
# from datetime import datetime, timedelta

# table_name = "botox_table"
# region_name = 'eu-west-1'

# # Initialize a session using Amazon DynamoDB
# session = boto3.session.Session(region_name=region_name)
# dynamodb = session.resource('dynamodb')

# # Initialize DynamoDB Resource
# table = dynamodb.Table(table_name)

# def create_appointments(date):
#     # Define appointment times
#     appointment_times = [(datetime.strptime(f"{date} {hour:02d}:00", '%Y-%m-%d %H:%M')).strftime('%Y-%m-%d %H:%M') 
#                          for hour in range(9, 18)]
    
#     with table.batch_writer() as batch:
#         for time in appointment_times:
#             appointment_id = f"{date.replace('-', '')}{time.replace(':', '')}"
#             appointment_time_range = f"{time}- {(datetime.strptime(time, '%Y-%m-%d %H:%M') + timedelta(hours=1)).strftime('%H:%M')}"
#             batch.put_item(
#                 Item={
#                     'id': appointment_id,
#                     'timestamp': time,
#                     'is_available': True,
#                     'user_cell_number': None,
#                     'user_full_name': None,
#                     'appointment_times': appointment_time_range
#                 }
#             )

# # Get today's date
# today = datetime.now()

# # Insert appointments for the next day
# appointment_date = (today + timedelta(days=1)).strftime('%Y-%m-%d')
# create_appointments(appointment_date)
