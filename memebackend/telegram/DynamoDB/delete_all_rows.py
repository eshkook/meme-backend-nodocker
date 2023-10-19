import boto3

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table('botox_table')

# Scan the table to get all item keys
response = table.scan(
    ProjectionExpression='#id, #ts',
    ExpressionAttributeNames={
        '#id': 'id',
        '#ts': 'timestamp'
    }
)
items = response['Items']

# Iterate through the keys and delete each item
for item in items:
    print(f"Deleting item {item['id']} at {item['timestamp']}...")
    table.delete_item(
        Key={
            'id': item['id'],
            'timestamp': item['timestamp']
        }
    )
print("All items deleted.")
