from botocore.exceptions import ClientError
import boto3
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

def reset_password_code_phase_handler(body):
    email = body['email']
    confirmation_code = body['confirmation_code']
    password = body['password']

    client = boto3.client('cognito-idp')
    # user_pool_id = 'eu-west-1_BZy97DfFY'
    client_id = '6be5bmss0rg7krjk5rd6dt28uc'

    try:
        client.confirm_forgot_password(
            ClientId=client_id,
            Username=email,
            ConfirmationCode=confirmation_code,
            Password=password
        )
        return {'statusCode': 200,
                'body': json.dumps('Password reset was successful.')}
    
    except ClientError as e:    
        logger.error("ClientError occurred: %s", e.response['Error']['Message'])
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}
    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')} # without this response, 
                                                                                     #  it can be interpretated as success by the mutation


