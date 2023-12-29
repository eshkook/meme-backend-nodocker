from botocore.exceptions import ClientError
import boto3
import json
from boto3.dynamodb.conditions import Attr
from timeout_decorator import timeout
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

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

        id_cookie = f'id_token={id_token}; HttpOnly; Secure; Path=/; SameSite=None'
        access_cookie = f'access_token={access_token}; HttpOnly; Secure; Path=/; SameSite=None'
        refresh_cookie = f'refresh_token={refresh_token}; HttpOnly; Secure; Path=/; SameSite=None'
    
        return {
            'statusCode': 200,
            'cookies': [id_cookie, access_cookie, refresh_cookie],
            'body': json.dumps('Login successful')
        }

    except ClientError as e:    
        logger.error("ClientError occurred: %s", e.response['Error']['Message'])
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}
    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}