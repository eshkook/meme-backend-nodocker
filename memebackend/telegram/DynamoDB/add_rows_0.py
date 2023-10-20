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
            'id': '1',  # Replace 'unique_id' with a unique value
            'timestamp': '1',  # Replace 'your_timestamp' with a timestamp value
            'a': 1,
            'b': 2,
            'c': 3
        }
    )

# Call the function to add a single row
create_entry()

