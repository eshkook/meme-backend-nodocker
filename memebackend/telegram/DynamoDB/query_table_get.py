import boto3

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table('botox_2_table')

def lookup_item(chat_id):
    response = table.get_item(
        Key={
            'id': chat_id
        }
    )
    item = response.get('Item')
    return item

# Example Usage:
chat_id = "1"
item = lookup_item(chat_id)
print(item)
