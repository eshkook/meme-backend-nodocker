from botocore.exceptions import ClientError
import boto3
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

def delete_handler(event):
    ################################################# test that cookies arrived in headers
    headers = event.get('headers', {})
    print('headers: ', headers)
    ########################################################
    body = json.loads(event['body'])
    password = body['password']
    cookies = event.get('headers', {}).get('Cookie', '')
    access_token = extract_token(cookies, 'access_token')
    refresh_token = extract_token(cookies, 'refresh_token')
    client = boto3.client('cognito-idp')

    # Try to validate the access token first
    if not access_token: 
        logger.error("access_token wasn't provided in cookies")
        return {'statusCode': 401, 'body': json.dumps("An internal error occurred")}
    
    try:
        # authentication:
        user_info = client.get_user(AccessToken=access_token)
        username = user_info['Username']
        # validating password:
        _ = client.admin_initiate_auth(
            UserPoolId = 'eu-west-1_BZy97DfFY',
            ClientId = client,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        # now we can delete account:
        client.admin_delete_user(
            UserPoolId='eu-west-1_BZy97DfFY',
            Username=username
        )
        return clear_tokens_response_200('Account Deletion Successful')

    except client.exceptions.NotAuthorizedException as e:
        # If Access token is invalid, try using the Refresh token
        if not refresh_token: 
            logger.error("refresh_token wasn't provided in cookies")
            return {'statusCode': 401, 'body': json.dumps("An internal error occurred")}
        
        try:
            # Refresh the access token using refresh token
            new_tokens = refresh_access_token(client, refresh_token)
            username = new_tokens['Username']
            # validating password:
            _ = client.admin_initiate_auth(
                UserPoolId = 'eu-west-1_BZy97DfFY',
                ClientId = client,
                AuthFlow='ADMIN_NO_SRP_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            # now we can delete account:
            client.admin_delete_user(
                UserPoolId='eu-west-1_BZy97DfFY',
                Username=username
            )
            return clear_tokens_response_200('Account Deletion Successful - Token Refreshed')
            
        except Exception as e:
            logger.error('Error refreshing token or deleting user: %s', e, exc_info=True)
            return clear_tokens_response_401('Session expired, please log in again. Account was not deleted.')

    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}