from botocore.exceptions import ClientError
import boto3
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

def signup_handler(body):
    email = body['email']
    password = body['password']
    first_name = body['first_name']
    last_name = body['last_name']

    client = boto3.client('cognito-idp')
    # user_pool_id = 'eu-west-1_BZy97DfFY'
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
            {
                'Name': 'given_name',
                'Value': first_name  
            },
            {
                'Name': 'family_name',
                'Value': last_name  
            }
        ]
    )

        return {'statusCode': 200,
                'body': json.dumps('User registration successful.')}
    
    except ClientError as e:    
        logger.error("ClientError occurred: %s", e.response['Error']['Message'])
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}
    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')} # without this response, 
                                                                                     #  it can be interpretated as success by the mutation
