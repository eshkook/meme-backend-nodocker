import boto3

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table('botox_3_table')

# 1. Scan the table
response = table.scan()
items = response['Items']

# Sort items by timestamp
# sorted_items = sorted(items, key=lambda x: x['timestamp'])

# print(sorted_items[1]['appointment_times'])

for item in items:
    print(item)

