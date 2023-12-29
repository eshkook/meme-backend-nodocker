from helper_functions.extract_token import extract_token 
from helper_functions.refresh_access_token import refresh_access_token 
from helper_functions.clear_tokens_response_401 import clear_tokens_response_401 

import boto3
import json
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

def authenticate_handler(event):
    cookies = event.get('headers', {}).get('Cookie', '')
    access_token = extract_token(cookies, 'access_token')
    refresh_token = extract_token(cookies, 'refresh_token')
    client = boto3.client('cognito-idp')

    # Try to validate the access token first
    if not access_token: 
        logger.error("access_token wasn't provided in cookies")
        return {'statusCode': 401, 'body': json.dumps("An internal error occurred")}
    
    try:
        user_info = client.get_user(AccessToken=access_token)
        first_name = next((attr['Value'] for attr in user_info['UserAttributes'] if attr['Name'] == 'given_name'), None)
        
        return {
            'statusCode': 200,
            'body': json.dumps({'message': 'Account Authentication Successful', 
                                'firstName': first_name})
        }

    except client.exceptions.NotAuthorizedException as e:
        # If Access token is invalid, try using the Refresh token
        if not refresh_token: 
            logger.error("refresh_token wasn't provided in cookies")
            return {'statusCode': 401, 'body': json.dumps("An internal error occurred")}
        
        try:
            # Refresh the access token using refresh token
            new_tokens = refresh_access_token(client, refresh_token)
            id_token = new_tokens['IdToken']
            access_token = new_tokens['AccessToken']
            
            updated_user_info = client.get_user(AccessToken=access_token)
            first_name = next((attr['Value'] for attr in updated_user_info['UserAttributes'] if attr['Name'] == 'given_name'), None)

            id_cookie = f'id_token={id_token}; HttpOnly; Secure; Path=/; SameSite=None'
            access_cookie = f'access_token={access_token}; HttpOnly; Secure; Path=/; SameSite=None'

            return {
                'statusCode': 200,
                'cookies': [id_cookie, access_cookie],
                # 'body': json.dumps('Account Authentication Successful - Token Refreshed'),
                'body': json.dumps({'message': 'Account Authentication Successful - Token Refreshed', 
                                    'firstName': first_name})
            }
            
        except Exception as e:
            logger.error('Error refreshing token: %s', e, exc_info=True)
            return clear_tokens_response_401('Session expired, please log in again. Account was not deleted.')

    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}


