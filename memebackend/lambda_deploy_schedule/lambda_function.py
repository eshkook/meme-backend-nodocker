#  creating a deployment package with dependencies:
# pip install requests -t .                 
# pip install timeout_decorator -t .
# pip install openai==0.28 -t .

# then zip all files in this directory besides urllib stuff, and upload to aws lambda:

# zip in powershell with command: 
# Get-ChildItem -Path . | Where-Object { $_.Name -notlike 'function.zip' } | Compress-Archive -DestinationPath function.zip -Force

# deploy this zip to aws lambda with command: 
# aws lambda update-function-code --function-name botox_function --zip-file fileb://function.zip

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

gpt_use_limit_per_user_per_day = 3

def lambda_handler(event, context):
    try:
        if "source" in event and event["source"] == "aws.events":
            handle_cloudwatch_event(event)
        else:
            handle_telegram_event(event)

        return {"statusCode": 200, "body": json.dumps("Success")}
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return {"statusCode": 500, "body": json.dumps("Error")}
    
def handle_cloudwatch_event(event): 
    # send the users in the database a message "Quiet"
    response = table.scan()
    items = response['Items']
    for item in items:
        chat_id = item['chat_id']
        payload = {
            "chat_id": str(chat_id),
            "text": f"Quiet",
        }
        response = requests.post(sendMessage_url, json=payload)

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

        if user_message == '/start':
            handle_start(chat_id)
        elif len(user_message) > 200:
            handle_long_messages(chat_id)
        else: 
            # check if user_id exists in database:
            item = table.get_item(Key={"id": str(user_id)})
            item = item.get("Item") 
            if item:
                # user_id exists, now check if limit was exceeded:
                gpt_use_counter = item['gpt_use_counter']
                if gpt_use_counter < gpt_use_limit_per_user_per_day:
                    # then we can use gpt and update the use counter:
                    handle_standard_messages(chat_id, user_message)
                    table.update_item(
                        Key={
                            "id": str(user_id),
                        },
                        UpdateExpression="SET gpt_use_counter = :new_gpt_use_counter",
                        ExpressionAttributeValues={":new_gpt_use_counter": gpt_use_counter + 1},
                    )
                else:
                    # tell the user they exceeded daily use limit
                    payload = {
                        "chat_id": chat_id,
                        "text": "חרגת מהשימוש היומי",
                    }
                    response = requests.post(sendMessage_url, json=payload)
            else:
                # user_id is not in database, let's create it and respond the user
                handle_standard_messages(chat_id, user_message)
                table.put_item(
                    Item={
                        "id": str(user_id),
                        "gpt_use_counter": 1,
                        "chat_id": str(chat_id)
                    }
                )            

    elif 'callback_query' in body:
        chat_id = body['callback_query']['message']['chat']['id']
        query_data = body['callback_query']['data']
        message_id = body['callback_query']['message']['message_id'] 
        user_info = body['callback_query']['message']['from']
        username = user_info.get('username', '')
        full_name = user_info.get('first_name', '') + " " + user_info.get('last_name', '')
        user_id = user_info['id']    

        # handle query logic
          
def handle_start(chat_id):
    payload = {
                    "chat_id": chat_id,
                    "text": "שלום! מה תרצה לעשות ?",
                }
    response = requests.post(sendMessage_url, json=payload)

def handle_long_messages(chat_id):
    payload = {
                    "chat_id": chat_id,
                    "text": "אנא כתוב הודעות קצרות יותר",
                }
    response = requests.post(sendMessage_url, json=payload)

def handle_standard_messages(chat_id, user_message):
    for j in range(3):
        try:
            response_text = chat_with_gpt(user_message)
            break
        except Exception as e:
            print(e)
            if j == 2:
                response_text = 'Sorry, some error occured, please write again'
            time.sleep(1)

    payload = {
                    "chat_id": chat_id,
                    "text": response_text,
               }
    response = requests.post(sendMessage_url, json=payload)          

@timeout(5)
def chat_with_gpt(input):
    instructions = '''
    which of the following does the input relate to: 
    Schedule an appointment/
    Reschedule an appointment/
    Cancel an appointment/
    Find out appointment time/
    Find out if appointment exists/
    Other.
    In your response always include only one of the options above (and in English).
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