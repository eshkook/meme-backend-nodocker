from botocore.exceptions import ClientError
import boto3
import json
import logging
from timeout_decorator import timeout
import openai
import time

# AWS DynamoDB setup
region_name = "eu-west-1"
table_name = "backend_user_table"
dynamodb = boto3.resource("dynamodb", region_name=region_name)
table = dynamodb.Table(table_name)

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.ERROR)  # You can set this to DEBUG, INFO, WARNING, ERROR

openai.api_key = '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' 

gpt_limit_per_user_per_day = 3

def gpt_handler(event):
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
                    'cookies': [id_cookie, access_cookie],
                    'body': json.dumps('You have exceeded your gpt usage limit')
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

@timeout(5)
def chat_with_gpt(input):
    instructions = '''
    Answer shortly.
    '''
    messages = [
        {"role": "system", "content": instructions},
        {"role": "user", "content": input[:200]}, # limit the input length
    ]
    response = openai.ChatCompletion.create(
        model='gpt-3.5-turbo',
        messages=messages,
        temperature=0,
        max_tokens=20
    )
    return response.choices[0].message['content']   

