from helper_functions.extract_token import extract_token 
from helper_functions.clear_tokens_response_200 import clear_tokens_response_200

import json
import logging
import boto3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

def logout_handler(event):
    try:
        return clear_tokens_response_200('Logout successful')
    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}

# def handle_logout(event):
#     cookies = event.get('headers', {}).get('Cookie', '')
#     access_token = extract_token(cookies, 'access_token')
#     client = boto3.client('cognito-idp')

#     if not access_token:
#         logger.error("access_token wasn't provided in cookies")
#         return {'statusCode': 401, 'body': json.dumps("An internal error occurred")}

#     try:
#         # Assuming you have a function to decode the JWT access token and extract the username
#         user_info = client.get_user(AccessToken=access_token)
#         username = user_info['Username']

#         # Using AdminUserGlobalSignOut to sign out the user globally
#         client.admin_user_global_sign_out(
#             UserPoolId='eu-west-1_BZy97DfFY',
#             Username=username
#         )

#         # Clear cookies and return a successful sign-out response
#         return clear_tokens_response_200('Logout successful')

#     except Exception as e:
#         logger.error('An error occurred: %s', e, exc_info=True)
#         return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}
    


