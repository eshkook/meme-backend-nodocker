#  creating a deployment package with dependencies:
# pip install timeout_decorator -t .
# pip install openai==0.28 -t .                

# then zip all files in this directory besides urllib stuff, and upload to aws lambda:

# zip in powershell with command: 
# Get-ChildItem -Path . | Where-Object { $_.Name -notlike 'function.zip' } | Compress-Archive -DestinationPath function.zip -Force

# deploy this zip to aws lambda with command: 
# aws lambda update-function-code --function-name backend_function --zip-file fileb://function.zip

from botocore.exceptions import ClientError
import boto3
import json
import logging
from boto3.dynamodb.conditions import Attr
from timeout_decorator import timeout
import openai
import time

openai.api_key = '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' 

gpt_limit_per_user_per_day = 3

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

# AWS DynamoDB setup
region_name = "eu-west-1"
table_name = "backend_user_table"
dynamodb = boto3.resource("dynamodb", region_name=region_name)
table = dynamodb.Table(table_name)

def lambda_handler(event, context):
    body = json.loads(event['body'])
    action = body.get('action')

    if "source" in event and event["source"] == "aws.events":
        handle_cloudwatch_event(event)
    elif action == 'signup':
        return handle_signup(body)
    elif action == 'confirm':
        return handle_confirmation(body)
    elif action == 'login':
        return handle_login(body)
    elif action == 'authenticate':
        return handle_authenticate(event)
    elif action == 'logout':
        return handle_logout(event)
    elif action == 'delete':
        return handle_delete(event)
    elif action == 'gpt':
        return handle_gpt(event)
    elif action == 'reset_password_email_phase':
        return handle_reset_password_email_phase(body)
    elif action == 'reset_password_code_phase':
        return handle_reset_password_code_phase(body)
    else:
        return {'statusCode': 400, 'body': json.dumps('Invalid action')}

@timeout(5)
def chat_with_gpt(input):
    instructions = '''
    Answer shortly.
    '''
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": input},
    ]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0,
        max_tokens=20
    )
    return response.choices[0].message['content']    

def handle_cloudwatch_event(event):
    pass

def handle_gpt(event):
    body = json.loads(event['body'])
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
        # check useage limit in DynamoDB:
        region_name = "eu-west-1"
        table_name = "gpt_users_table" # gpt_ip_table
        dynamodb = boto3.resource("dynamodb", region_name=region_name)
        table = dynamodb.Table(table_name)
        response = table.get_item(
            Key={
                'id': username
            }
        )
        item = response.get('Item')
        if not item:
            table.put_item(
                Item={
                    'id': username,
                    'usage': 1 
                }
            )
        elif item['usage'] < gpt_limit_per_user_per_day:
            old_usage = item['usage']
            table.update_item(
                    Key={
                        "id": username,
                    },
                    UpdateExpression="SET usage = :usage",
                    ExpressionAttributeValues={":usage": old_usage + 1},
                )
        else:
            return {
                'statusCode': 429,
                'body': json.dumps('You have exceeded your usage limit')
            }
        
        # now we can go to chatGPT:
        prompt = body['prompt']
        for j in range(3):
            try:
                response_text = chat_with_gpt(prompt)
                break
            except Exception as e:
                print(e)
                if j == 2:
                    response_text = 'Sorry, some error occured, please try again'
                time.sleep(1)
        return {'statusCode': 200, 'body': json.dumps(response_text)} 

    except client.exceptions.NotAuthorizedException as e:
        # If Access token is invalid, try using the Refresh token
        if not refresh_token: 
            logger.error("refresh_token wasn't provided in cookies")
            return {'statusCode': 401, 'body': json.dumps("An internal error occurred")}

        try:
            # Refresh the access token using refresh token
            new_tokens = refresh_access_token(client, refresh_token)
            username = new_tokens['Username']
            id_token = new_tokens['IdToken'] #?????????????

            access_token = new_tokens['AccessToken'] 
            id_cookie = f'id_token={id_token}; HttpOnly; Secure; Path=/; SameSite=None'
            access_cookie = f'access_token={access_token}; HttpOnly; Secure; Path=/; SameSite=None'
            
            # check useage limit in DynamoDB:
            region_name = "eu-west-1"
            table_name = "gpt_users_table"
            dynamodb = boto3.resource("dynamodb", region_name=region_name)
            table = dynamodb.Table(table_name)
            response = table.get_item(
                Key={
                    'id': username
                }
            )
            item = response.get('Item')
            if not item:
                table.put_item(
                    Item={
                        'id': username,
                        'usage': 1 
                    }
                )
            elif item['usage'] < gpt_limit_per_user_per_day:
                old_usage = item['usage']
                table.update_item(
                        Key={
                            "id": username,
                        },
                        UpdateExpression="SET usage = :usage",
                        ExpressionAttributeValues={":usage": old_usage + 1},
                    )
            else:
                return {
                    'statusCode': 429,
                    'cookies': [id_cookie, access_cookie,],
                    'body': json.dumps('You have exceeded your usage limit')
                }             
            
            # now we can go to chatGPT:
            prompt = body['prompt']
            for j in range(3):
                try:
                    response_text = chat_with_gpt(prompt)
                    break
                except Exception as e:
                    print(e)
                    if j == 2:
                        response_text = 'Sorry, some error occured, please try again'
                    time.sleep(1)
            return {
                'statusCode': 200,
                'cookies': [id_cookie, access_cookie],
                'body': json.dumps(response_text)
            }
            
        except Exception as e:
            logger.error('Error refreshing token or deleting user: %s', e, exc_info=True)
            return clear_tokens_response_401('Session expired, please log in again. Account was not deleted.')

    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}

def handle_reset_password_code_phase(body):
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

def handle_reset_password_email_phase(body):
    email = body['email']

    client = boto3.client('cognito-idp')
    # user_pool_id = 'eu-west-1_BZy97DfFY'
    client_id = '6be5bmss0rg7krjk5rd6dt28uc'

    try:
        client.forgot_password(
            ClientId=client_id,
            Username=email
        )
        return {'statusCode': 200,
                'body': json.dumps('Asking for code to reset password was successful.')}
    
    except ClientError as e:    
        logger.error("ClientError occurred: %s", e.response['Error']['Message'])
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}
    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')} # without this response, 
                                                                                     #  it can be interpretated as success by the mutation

def handle_signup(body):
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
        logger.error("ClientError occurred: %s", e.response['Error']['Message'])
        return {'statusCode': 400, 'body': json.dumps(e.response['Error']['Message'])}
    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}

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

def handle_authenticate(event):
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

        return {
            'statusCode': 200,
            'body': json.dumps('Account Authentication Successful')
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

            id_cookie = f'id_token={id_token}; HttpOnly; Secure; Path=/; SameSite=None'
            access_cookie = f'access_token={access_token}; HttpOnly; Secure; Path=/; SameSite=None'

            return {
                'statusCode': 200,
                'cookies': [id_cookie, access_cookie],
                'body': json.dumps('Account Authentication Successful - Token Refreshed')
            }
            
        except Exception as e:
            logger.error('Error refreshing token: %s', e, exc_info=True)
            return clear_tokens_response_401('Session expired, please log in again. Account was not deleted.')

    except Exception as e:
        logger.error('An error occurred: %s', e, exc_info=True)
        return {'statusCode': 500, 'body': json.dumps('An internal error occurred')}

def handle_logout(event):
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

def handle_delete(event):
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

def clear_tokens_response_200(message):
    access_cookie = 'access_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
    id_cookie = 'id_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
    refresh_cookie = 'refresh_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'

    return {
            'statusCode': 200,
            'cookies': [id_cookie, access_cookie, refresh_cookie],
            'body': json.dumps(message)
        }

def clear_tokens_response_401(message):
    access_cookie = 'access_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
    id_cookie = 'id_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'
    refresh_cookie = 'refresh_token=; HttpOnly; Secure; Path=/; SameSite=None; Expires=Thu, 01 Jan 1970 00:00:00 GMT'

    return {
        'statusCode': 401,
        'cookies': [id_cookie, access_cookie, refresh_cookie],
        'body': json.dumps('Login successful')
    }

def refresh_access_token(client, refresh_token, client_id):
    try:
        response = client.admin_initiate_auth(
            UserPoolId='eu-west-1_BZy97DfFY',
            ClientId=client_id,
            AuthFlow='REFRESH_TOKEN_AUTH',
            AuthParameters={
                'REFRESH_TOKEN': refresh_token
            }
        )
        new_access_token = response['AuthenticationResult']['AccessToken']
        new_id_token = response['AuthenticationResult']['IdToken']
        # Extract username or other details as needed
        user_info = client.get_user(AccessToken=new_access_token)
        username = user_info['Username']

        return {
            'AccessToken': new_access_token,
            'IdToken': new_id_token,
            'Username': username
        }

    except ClientError as e:
        raise e  # Re-raise the exception to handle it in the calling function

def extract_token(cookies, token_name):
    for cookie in cookies.split(';'):
        parts = cookie.strip().split('=')
        if parts[0] == token_name and len(parts) > 1:
            return parts[1]
    return None
