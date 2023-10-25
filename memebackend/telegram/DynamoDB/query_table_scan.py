import boto3
from boto3.dynamodb.conditions import Attr

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table('botox_3_table')

# # 1. Scan the table
# response = table.scan()
# items = response['Items']

# # Sort items by timestamp
# # sorted_items = sorted(items, key=lambda x: x['timestamp'])

# # print(sorted_items[1]['appointment_times'])

# for item in items:
#     print(item)




# response = table.scan()
# items = response.get('Items', [])
# scheduled_slots = [item for item in items if (item.get('chat_id') and item['chat_id'])]

# if scheduled_slots:
#     sorted_scheduled_slots = sorted(scheduled_slots, key=lambda x: x['appointment_times'])
#     calendar_summary = "Calendar:"
#     for scheduled_slot in sorted_scheduled_slots:
#         calendar_summary += f"\n\nappointment_times: {scheduled_slot['appointment_times']}, chat_id: {scheduled_slot['chat_id']}"
# else:
#         calendar_summary = "No scheduled appointments."

# print(calendar_summary)    


response = table.scan(
    FilterExpression=Attr('chat_id').exists() & Attr('chat_id').ne(None)
)
scheduled_slots = response.get('Items', [])

if scheduled_slots:
    sorted_scheduled_slots = sorted(scheduled_slots, key=lambda x: x['appointment_times'])
    calendar_summary = "Calendar:"
    for scheduled_slot in sorted_scheduled_slots:
        calendar_summary += f"\n\nappointment_times: {scheduled_slot['appointment_times']}, chat_id: {scheduled_slot['chat_id']}"
else:
    calendar_summary = "No scheduled appointments."

print(calendar_summary)  
          