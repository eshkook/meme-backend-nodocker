import boto3

# Initialize a session using Amazon DynamoDB
session = boto3.session.Session(region_name='eu-west-1')
dynamodb = session.resource('dynamodb')

# Initialize DynamoDB Resource
table = dynamodb.Table('botox_3_table')

def lookup_item(id):
    response = table.get_item(
        Key={
            'id': id
        }
    )
    item = response.get('Item')
    return item

# Example Usage:
id = '3'
item = lookup_item(id)
print(item)
