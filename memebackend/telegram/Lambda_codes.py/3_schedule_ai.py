import boto3
import json
import requests
import traceback
from boto3.dynamodb.conditions import Attr
from datetime import datetime, timedelta
import dateutil.tz
import time
from timeout_decorator import timeout
import openai

# AWS DynamoDB setup
region_name = "eu-west-1"
table_name = "botox_3_table"
dynamodb = boto3.resource("dynamodb", region_name=region_name)
table = dynamodb.Table(table_name)
israel_tz = dateutil.tz.gettz("Asia/Jerusalem")

# Telegram setup
telegram_token = "6467965504:AAHoFv-gir5CNKY8ZJvD-oaj0yYwseuTMmg"
api_url = f"https://api.telegram.org/bot{telegram_token}"
sendMessage_url = f"{api_url}/sendMessage"
edit_url = f"{api_url}/editMessageText"
delete_url = f"{api_url}/deleteMessage"

openai.api_key = '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' 

def lambda_handler(event, context):
    try:
        if "source" in event and event["source"] == "aws.events":
            handle_cloudwatch_event(event)
        elif "httpMethod" in event:
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

        if user_message == '/start':
            handle_start(chat_id)
        elif len(user_message) > 200:
            handle_long_messages(chat_id)
        else:    
            handle_standard_messages(chat_id, user_message)
            
    elif 'callback_query' in body:
        chat_id = body['callback_query']['message']['chat']['id']
        query_data = body['callback_query']['data']
        message_id = body['callback_query']['message']['message_id'] 
        user_info = body['callback_query']['message']['from']
        username = user_info.get('username', '')
        full_name = user_info.get('first_name', '') + " " + user_info.get('last_name', '')    

        # handle query logic
          
def handle_start(chat_id):
    payload = {
                    "chat_id": str(chat_id),
                    "text": "שלום! מה תרצה לעשות ?",
                }
    response = requests.post(sendMessage_url, json=payload)

def handle_long_messages(chat_id):
    payload = {
                    "chat_id": str(chat_id),
                    "text": "אנא כתוב הודעות קצרות יותר",
                }
    response = requests.post(sendMessage_url, json=payload)

def handle_standard_messages(chat_id, user_message):
    response_text = chat_with_gpt(user_message)
    payload = {
                    "chat_id": str(chat_id),
                    "text": response_text,
                }
    response = requests.post(sendMessage_url, json=payload)          

@timeout(10)
def chat_with_gpt(input):
    instructions = 'which of the following does the input relate to: Schedule an appointment/Reschedule an appointment/Canceling an appointment/Other' 
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