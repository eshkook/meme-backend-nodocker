import boto3
from datetime import datetime, timedelta
import dateutil.tz

table_name = "botox_3_table"
region_name = 'eu-west-1'

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name=region_name)
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table(table_name)

def create_appointments():
    slots_list = []
    israel_tz = dateutil.tz.gettz('Asia/Jerusalem')
    now_datetime = datetime.now(israel_tz)
    today_at_9_datetime = now_datetime.replace(hour=9, minute=0, second=0, microsecond=0)
    # for work_hours in range(9): 
    #     potential_slot_datetime = today_at_9_datetime + timedelta(hours=work_hours)
    #     if now_datetime < potential_slot_datetime:
    #         slots_list.append(potential_slot_datetime)

    tomorrow_at_9_datetime = today_at_9_datetime + timedelta(days=1)
    for work_hours in range(9): 
        slots_list.append(tomorrow_at_9_datetime + timedelta(hours=work_hours))

    for slot in slots_list:
        table.put_item(
            Item={
                'id': slot.strftime('%Y-%m-%d %H:%M'),
                'is_available': True,
                'chat_id': None,
                'username': None,
                'full_name': None,
                'appointment_times': slot.strftime('%Y-%m-%d %H:%M') + '-' + (slot + timedelta(hours=1)).strftime('%H:%M')
            }
        )    

create_appointments()
