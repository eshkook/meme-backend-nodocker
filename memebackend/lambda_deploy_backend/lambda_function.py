#  creating a deployment package with dependencies:
# pip install ????? -t .                 

# then zip all files in this directory besides urllib stuff, and upload to aws lambda:

# zip in powershell with command: 
# Get-ChildItem -Path . | Where-Object { $_.Name -notlike 'function.zip' } | Compress-Archive -DestinationPath function.zip -Force

# deploy this zip to aws lambda with command: 
# aws lambda update-function-code --function-name backend_function --zip-file fileb://function.zip

from botocore.exceptions import ClientError
import boto3
import json
from boto3.dynamodb.conditions import Attr

# AWS DynamoDB setup
region_name = "eu-west-1"
table_name = "backend_user_table"
dynamodb = boto3.resource("dynamodb", region_name=region_name)
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    body = json.loads(event['body'])
    action = body.get('action')

    if action == 'signup':
        return handle_signup(body)
    elif action == 'confirm':
        return handle_confirmation(body)
    elif action == 'login':
        return handle_login(body)
    else:
        return {'statusCode': 400, 'body': json.dumps('Invalid action')}

def handle_signup(body):
    email = body['email']
    password = body['password']

    client = boto3.client('cognito-idp')
    user_pool_id = 'eu-west-1_BZy97DfFY'
    client_id = '6be5bmss0rg7krjk5rd6dt28uc'

    try:
        response = client.sign_up(
            ClientId=client_id,
            Username=email,
            Password=password,
            UserAttributes=[
                {
                    'Name': 'email',
                    'Value': email
                },
            ]
        )
        return {'statusCode': 200,
                'body': json.dumps('User registration successful.')}
    except ClientError as e:
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}

def handle_confirmation(body):
    email = body['email']
    confirmation_code = body['confirmation_code']
    client = boto3.client('cognito-idp')
    client_id = '6be5bmss0rg7krjk5rd6dt28uc'

    try:
        response = client.confirm_sign_up(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=confirmation_code
        )
        return {'statusCode': 200, 'body': json.dumps('Confirmation successful.')}
    except ClientError as e:
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}

def handle_login(body):
    email = body['email']
    password = body['password']

    client = boto3.client('cognito-idp')
    client_id = '6be5bmss0rg7krjk5rd6dt28uc'

    try:
        response = client.admin_initiate_auth(
            UserPoolId='eu-west-1_BZy97DfFY',
            ClientId=client_id,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': password
            }
        )

        id_token = response['AuthenticationResult']['IdToken']
        access_token = response['AuthenticationResult']['AccessToken']
        refresh_token = response['AuthenticationResult']['RefreshToken']

        # Construct cookie strings
        # For local development (no 'Secure' attribute)
        # id_cookie = f'id_token={id_token}; HttpOnly; Path=/; SameSite=None'
        # access_cookie = f'access_token={access_token}; HttpOnly; Path=/; SameSite=None'
        # refresh_cookie = f'refresh_token={refresh_token}; HttpOnly; Path=/; SameSite=None'

        # Uncomment the following lines for production (with 'Secure' attribute)
        id_cookie = f'id_token={id_token}; HttpOnly; Secure; Path=/; SameSite=None'
        access_cookie = f'access_token={access_token}; HttpOnly; Secure; Path=/; SameSite=None'
        refresh_cookie = f'refresh_token={refresh_token}; HttpOnly; Secure; Path=/; SameSite=None'

        # id_cookie = f'id_token={id_token}; HttpOnly; Secure; Path=/; SameSite=None'
        # access_cookie = f'access_token={access_token}; HttpOnly; Secure; Path=/; SameSite=None'
        # refresh_cookie = f'refresh_token={refresh_token}; HttpOnly; Secure; Path=/; SameSite=None'

        # Concatenate cookies for the header
        cookie_header = f'{id_cookie}, {access_cookie}, {refresh_cookie}'

        return {
            'statusCode': 200,
            'headers': {
                'Set-Cookie': cookie_header
            },
            'body': json.dumps('Login successful')
        }

        # return {
        #     'statusCode': 200,
        #     'headers': {
        #         'Set-Cookie': cookie_header,
        #         'Access-Control-Allow-Origin': 'https://main.d2sw1m24xot5cm.amplifyapp.com/',  
        #         'Access-Control-Allow-Credentials': 'true'  
        #     },
        #     'body': json.dumps('Login successful')
        # }

    except ClientError as e:
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}

    
