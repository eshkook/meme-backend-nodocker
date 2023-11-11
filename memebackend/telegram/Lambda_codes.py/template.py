import boto3
import json
import requests
import traceback  
from boto3.dynamodb.conditions import Attr

# AWS DynamoDB setup
region_name = '????????'
table_name = '???????????????????'
dynamodb = boto3.resource('dynamodb', region_name=region_name)
table = dynamodb.Table(table_name)

# Telegram setup
telegram_token = '????????????????'
api_url = f'https://api.telegram.org/bot{telegram_token}'
sendMessage_url = f'{api_url}/sendMessage'
edit_url = f'{api_url}/editMessageText'
delete_url = f'{api_url}/deleteMessage'

def lambda_handler(event, context):
    try:
        if 'source' in event and event['source'] == 'aws.events':
            handle_cloudwatch_event(event)
        elif 'httpMethod' in event and event['headers'].get('Content-Type') == 'application/json':
            return handle_react_app_event(event)
        else:
            handle_telegram_event(event)
            
        return {"statusCode": 200, "body": json.dumps("Success")}
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps("Error")}

def handle_react_app_event(event):
    # handle react logic
    return {
        "statusCode": 200,
        "body": json.dumps(9)  # Converts the number 9 into a JSON-formatted string
    }

def handle_cloudwatch_event(event): 
    pass

def handle_telegram_event(event):
    body = json.loads(event['body'])
    
    if 'message' in body:
        chat_id = body['message']['chat']['id']
        user_message = body['message'].get('text', '')
        message_id = body['message']['message_id']
        user_info = body['message']['from']
        username = user_info.get('username', '')
        full_name = user_info.get('first_name', '') + " " + user_info.get('last_name', '')   
        user_id = user_info['id']

        # handle message logic

    elif 'callback_query' in body:
        chat_id = body['callback_query']['message']['chat']['id']
        query_data = body['callback_query']['data']
        message_id = body['callback_query']['message']['message_id'] 
        user_info = body['callback_query']['message']['from']
        username = user_info.get('username', '')
        full_name = user_info.get('first_name', '') + " " + user_info.get('last_name', '')    
        user_id = user_info['id']

        # handle query logic